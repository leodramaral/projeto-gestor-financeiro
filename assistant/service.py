"""One question to the model: the tool-calling loop and the checks on what comes out.

It knows nothing about HTTP or the session; the view passes the history in and records what it
returns. Every outcome carries the tokens spent, and so does every error, so the caller can count
them even when a later call fails.
"""

from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone
from openai import APIError, RateLimitError

from . import messages
from .client import get_client
from .guard import NO_QUERY, check_answer
from .prompts import system_prompt
from .tools import DECLINE, SMALLTALK, TOOLS, run_tool

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


@dataclass(frozen=True)
class Answer:
    """`text` is the model's answer when `outcome` is TEXT, and a fixed message otherwise."""

    outcome: str
    text: str
    tokens: int
    reason: str | None = None


class AssistantError(Exception):
    """The provider failed; `tokens` is what the earlier calls of the question already spent."""

    message = messages.UNAVAILABLE

    def __init__(self, tokens=0, cause=None, status=None):
        super().__init__(type(self).__name__)
        self.tokens = tokens
        self.cause = cause or type(self).__name__  # what failed, for the log (never content)
        self.status = status  # HTTP status of the provider, when it answered


class RateLimited(AssistantError):
    message = messages.RATE_LIMITED


class Unavailable(AssistantError):
    message = messages.UNAVAILABLE


def _clean(history):
    return [{"role": m["role"], "content": m["content"]} for m in history[-MAX_HISTORY_MESSAGES:]]


def _assistant_message(message):
    return {
        "role": "assistant",
        "content": message.content,
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {"name": call.function.name, "arguments": call.function.arguments},
            }
            for call in message.tool_calls
        ],
    }


class _Question:
    def __init__(self, user, history, question):
        self.user = user
        self.messages = [
            {"role": "system", "content": system_prompt(timezone.localdate())},
            *_clean(history),
            {"role": "user", "content": question},
        ]
        self.tokens = 0
        self.results = []  # spending results that worked, for this question only

    def run(self):
        """Whatever goes wrong becomes `Unavailable` with the tokens spent so far: an odd reply
        from the provider (an HTML page, a null field) must not end as a 500 that loses them."""
        try:
            return self._loop()
        except AssistantError:
            raise
        except Exception as error:
            raise Unavailable(self.tokens, type(error).__name__) from None

    def _loop(self):
        client = get_client()
        for number in range(MAX_MODEL_CALLS):
            message = self._ask(client, first=number == 0)
            if not message.tool_calls:
                return self._finish(message.content)
            refused = self._use_tools(message)
            if refused:
                return refused
        raise Unavailable(self.tokens)

    def _ask(self, client, first):
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
            raise RateLimited(self.tokens, type(error).__name__, error.status_code) from None
        except APIError as error:
            status = getattr(error, "status_code", None)
            raise Unavailable(self.tokens, type(error).__name__, status) from None
        self.tokens += getattr(response.usage, "total_tokens", None) or 0
        if not response.choices:
            raise Unavailable(self.tokens)
        choice = response.choices[0]
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
            if outcome.decline:
                return self._refused(outcome.decline)
            if outcome.data:
                self.results.append(outcome.data)
            self.messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": outcome.content}
            )
        return None

    def _refused(self, kind):
        text = messages.HELP if kind == SMALLTALK else messages.REFUSAL
        return Answer(REFUSED, text, self.tokens, reason=kind)

    def _finish(self, text):
        text = (text or "").strip()
        if not text:
            raise Unavailable(self.tokens)
        reason = check_answer(text, self.results)
        if reason:
            fixed = messages.REFUSAL if reason == NO_QUERY else messages.UNRELIABLE
            return Answer(REJECTED, fixed, self.tokens, reason=reason)
        return Answer(TEXT, text, self.tokens)


def answer(user, history, question):
    """Asks the model `question` for `user`, with the last messages of the conversation.

    Raises `RateLimited` or `Unavailable` when the provider fails (or has no key configured).
    """
    if not settings.LLM_API_KEY:
        raise Unavailable(cause="NoApiKey")
    return _Question(user, history, question).run()
