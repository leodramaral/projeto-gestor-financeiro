"""One question to the model: the tool-calling loop and the checks on what comes out.

It knows nothing about HTTP or the session; the view passes the history in and records what it
returns. Every outcome carries the tokens spent, and so does every error, so the caller can count
them even when a later call fails.
"""

import logging
import time
import uuid
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone
from openai import APIError, RateLimitError

from . import messages
from .client import get_client
from .guard import NO_QUERY, check_answer
from .prompts import system_prompt
from .tools import DECLINE, SMALLTALK, SPENDING, TOOLS, run_tool

logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 6
# Model calls per question: three rounds of tools and the final answer.
MAX_MODEL_CALLS = 4
# Output budget per call, with room for the reasoning the gpt-oss models spend before answering.
MAX_COMPLETION_TOKENS = 1024
# The first call must be a tool call, so the model never starts with free text (Groq accepts
# "required" with gpt-oss-120b; with "auto" the parameter is left out).
FIRST_ROUND_TOOL_CHOICE = "required"

TEXT = "text"
REFUSED = "refused"
REJECTED = "rejected"

# What the log keeps of the provider's error message on a 4xx.
MAX_PROVIDER_MESSAGE = 500
KNOWN_TOOLS = (SPENDING, DECLINE)


@dataclass(frozen=True)
class Answer:
    """`text` is the model's answer when `outcome` is TEXT, and a fixed message otherwise."""

    outcome: str
    text: str
    tokens: int
    reason: str | None = None
    question_id: str = ""
    rounds: int = 0


class AssistantError(Exception):
    """The provider failed; `tokens` is what the earlier calls of the question already spent."""

    message = messages.UNAVAILABLE

    def __init__(self, tokens=0, cause=None, status=None, detail=""):
        super().__init__(type(self).__name__)
        self.tokens = tokens
        self.cause = cause or type(self).__name__  # what failed, for the log (never content)
        self.status = status  # HTTP status of the provider, when it answered
        self.detail = detail  # the provider's message on a 4xx, cleaned (see `provider_message`)
        self.question_id = ""
        self.round = 0  # the model call that failed, counting from 1 (0: before the first)


class RateLimited(AssistantError):
    message = messages.RATE_LIMITED


class Unavailable(AssistantError):
    message = messages.UNAVAILABLE


def provider_message(error):
    """The message the provider sent with a 4xx error, safe to log: one line, the API key masked
    and cut short. Empty for any other error, and for a body that is not the expected shape: this
    runs while handling a failure, so it never raises."""
    status = getattr(error, "status_code", None)
    if not isinstance(status, int) or not 400 <= status < 500:
        return ""
    try:
        body = error.body
        if isinstance(body, list):
            body = body[0]
        text = body["error"]["message"]
        if not isinstance(text, str):
            return ""
        text = " ".join(text.split())
        if settings.LLM_API_KEY:
            text = text.replace(settings.LLM_API_KEY, "***")
        return text[:MAX_PROVIDER_MESSAGE]
    except (AttributeError, IndexError, KeyError, TypeError):
        return ""


def _clean(history):
    return [{"role": m["role"], "content": m["content"]} for m in history[-MAX_HISTORY_MESSAGES:]]


def _tool_call(call):
    """One tool call as it goes back to the provider: the standard fields plus whatever else the
    provider sent with it (the SDK keeps those in `model_extra`). Some providers hand over state
    in those fields and refuse the next round without it, so it is returned as received."""
    standard = {
        "id": call.id,
        "type": "function",
        "function": {"name": call.function.name, "arguments": call.function.arguments},
    }
    extra = getattr(call, "model_extra", None) or {}
    return {**extra, **standard}


def _assistant_message(message):
    return {
        "role": "assistant",
        "content": message.content,
        "tool_calls": [_tool_call(call) for call in message.tool_calls],
    }


class _Question:
    def __init__(self, user, history, question):
        self.user = user
        self.messages = [
            {"role": "system", "content": system_prompt(timezone.localdate())},
            *_clean(history),
            {"role": "user", "content": question},
        ]
        self.id = uuid.uuid4().hex[:8]  # ties the log lines of one question; carries no content
        self.round = 0
        self.tokens = 0
        self.results = []  # spending results that worked, for this question only

    def run(self):
        """Whatever goes wrong becomes `Unavailable` with the tokens spent so far: an odd reply
        from the provider (an HTML page, a null field) must not end as a 500 that loses them."""
        try:
            return self._loop()
        except AssistantError as error:
            self._stamp(error)
            raise
        except Exception as error:
            failure = Unavailable(self.tokens, type(error).__name__)
            self._stamp(failure)
            raise failure from None

    def _stamp(self, error):
        error.question_id = self.id
        error.round = self.round

    def _loop(self):
        client = get_client()
        for number in range(1, MAX_MODEL_CALLS + 1):
            self.round = number
            message = self._ask(client, number)
            if not message.tool_calls:
                return self._finish(message.content)
            refused = self._use_tools(message)
            if refused:
                return refused
        raise Unavailable(self.tokens)

    def _ask(self, client, number):
        first = number == 1
        started = time.monotonic()
        options = {}
        if first and FIRST_ROUND_TOOL_CHOICE != "auto":
            options["tool_choice"] = FIRST_ROUND_TOOL_CHOICE
        try:
            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=list(self.messages),
                tools=TOOLS,
                max_completion_tokens=MAX_COMPLETION_TOKENS,
                **options,
            )
        except RateLimitError as error:
            failure = RateLimited(
                self.tokens, type(error).__name__, error.status_code, provider_message(error)
            )
            failure.round = number
            raise failure from None
        except APIError as error:
            status = getattr(error, "status_code", None)
            failure = Unavailable(
                self.tokens, type(error).__name__, status, provider_message(error)
            )
            failure.round = number
            raise failure from None
        spent = getattr(response.usage, "total_tokens", None) or 0
        self.tokens += spent
        choice = response.choices[0] if response.choices else None
        logger.info(
            "Model call: id=%s round=%s model=%s finish_reason=%s tokens=%s seconds=%.2f",
            self.id,
            number,
            settings.LLM_MODEL,
            getattr(choice, "finish_reason", None),
            spent,
            time.monotonic() - started,
        )
        if choice is None:
            raise Unavailable(self.tokens)
        if getattr(choice, "finish_reason", None) == "length":
            raise Unavailable(self.tokens, "Truncated")  # cut off by max_completion_tokens
        return choice.message

    def _use_tools(self, message):
        """Runs the tools the model asked for. A refusal wins: nothing else runs and it is
        returned; otherwise the results go back to the model and None is returned."""
        calls = sorted(message.tool_calls, key=lambda call: call.function.name != DECLINE)
        self.messages.append(_assistant_message(message))
        for call in calls:
            outcome = run_tool(self.user, call.function.name, call.function.arguments)
            self._log_tool(call.function.name, outcome)
            if outcome.decline:
                return self._refused(outcome.decline)
            if outcome.data:
                self.results.append(outcome.data)
            self.messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": outcome.content}
            )
        return None

    def _log_tool(self, name, outcome):
        """Name and result only: the arguments and the data are the user's. The name comes from
        the model, so anything but a known tool is logged as `unknown`."""
        result = "refused" if outcome.decline else "ok" if outcome.data else "error"
        logger.info(
            "Tool call: id=%s round=%s tool=%s result=%s",
            self.id,
            self.round,
            name if name in KNOWN_TOOLS else "unknown",
            result,
        )

    def _refused(self, kind):
        text = messages.HELP if kind == SMALLTALK else messages.REFUSAL
        return Answer(REFUSED, text, self.tokens, kind, self.id, self.round)

    def _finish(self, text):
        text = (text or "").strip()
        if not text:
            raise Unavailable(self.tokens)
        reason = check_answer(text, self.results)
        if reason:
            fixed = messages.REFUSAL if reason == NO_QUERY else messages.UNRELIABLE
            return Answer(REJECTED, fixed, self.tokens, reason, self.id, self.round)
        return Answer(TEXT, text, self.tokens, None, self.id, self.round)


def answer(user, history, question):
    """Asks the model `question` for `user`, with the last messages of the conversation.

    Raises `RateLimited` or `Unavailable` when the provider fails (or has no key configured).
    """
    if not settings.LLM_API_KEY:
        raise Unavailable(cause="NoApiKey")
    return _Question(user, history, question).run()
