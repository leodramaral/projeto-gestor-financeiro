import logging
import time

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from . import messages
from .forms import QuestionForm
from .models import reserve_tokens, settle_tokens, tokens_used_today
from .service import MAX_HISTORY_MESSAGES, TEXT, AssistantError, answer

logger = logging.getLogger(__name__)

SESSION_KEY = "assistant_conversation"
# Held from the daily credit while a question runs: about what the longest one spends.
RESERVED_TOKENS = 4000

# A turn that never reaches the session: a fixed answer from the assistant, or an error line.
ASSISTANT, ERROR = "assistant", "error"
# Credit meter tones by percent used; the first whose floor is reached wins.
TONES = ((100, "critical"), (90, "error"), (70, "warning"), (0, "brand"))


def meter_tone(percent):
    return next(tone for floor, tone in TONES if percent >= floor)


class ChatView(LoginRequiredMixin, View):
    """The conversation lives in the session: the last few messages, text only, and nothing else."""

    template_name = "assistant/chat.html"

    def get(self, request):
        return self._render(request, QuestionForm())

    def post(self, request):
        form = QuestionForm(request.POST)
        if not form.is_valid() or not settings.LLM_API_KEY:
            return self._render(request, form)
        reservation = reserve_tokens(request.user, RESERVED_TOKENS, settings.LLM_DAILY_TOKEN_LIMIT)
        if reservation is None:
            return self._render(request, form, composer_notice=messages.NO_CREDITS)
        question = form.cleaned_data["question"]
        history = request.session.get(SESSION_KEY, [])
        started = time.monotonic()
        spent, failure = 0, None
        try:
            result = answer(request.user, history, question)
            spent = result.tokens
        except AssistantError as error:
            failure, spent = error, error.tokens
        finally:
            settle_tokens(reservation, RESERVED_TOKENS, spent)
        seconds = time.monotonic() - started
        if failure:
            logger.warning(
                "Assistant failure: id=%s round=%s model=%s cause=%s status=%s seconds=%.2f"
                " provider_message=%s",
                failure.question_id,
                failure.round,
                settings.LLM_MODEL,
                failure.cause,
                failure.status,
                seconds,
                failure.detail,
            )
            self._log_summary(failure.question_id, "failed", failure.round, spent, seconds)
            return self._render(request, form, turn=(question, ERROR, failure.message))
        self._log_summary(result.question_id, result.outcome, result.rounds, spent, seconds)
        if result.outcome != TEXT:
            logger.info("Assistant declined: reason=%s tokens=%s", result.reason, result.tokens)
            return self._render(request, QuestionForm(), turn=(question, ASSISTANT, result.text))
        history = [
            *history,
            {"role": "user", "content": question},
            {"role": "assistant", "content": result.text},
        ]
        request.session[SESSION_KEY] = history[-MAX_HISTORY_MESSAGES:]
        return redirect("assistant:chat")

    @staticmethod
    def _log_summary(question_id, outcome, rounds, tokens, seconds):
        logger.info(
            "Assistant question: id=%s outcome=%s rounds=%s tokens=%s seconds=%.2f",
            question_id,
            outcome,
            rounds,
            tokens,
            seconds,
        )

    def _render(self, request, form, turn=None, composer_notice=None):
        """`turn` is (question, kind, text): shown once, after the conversation, never stored.

        The text goes back to the field unless the assistant answered the question.
        """
        used = tokens_used_today(request.user)
        limit = settings.LLM_DAILY_TOKEN_LIMIT
        percent = min(100, used * 100 // limit) if limit else 100
        if composer_notice is None and not settings.LLM_API_KEY:
            composer_notice = messages.UNAVAILABLE
        if composer_notice is None and percent >= 100:
            composer_notice = messages.NO_CREDITS
        ephemeral = None
        if turn:
            question, kind, text = turn
            ephemeral = {"question": question, "kind": kind, "text": text}
        context = {
            "form": form,
            "conversation": request.session.get(SESSION_KEY, []),
            "ephemeral": ephemeral,
            "composer_notice": composer_notice,
            "restore": bool(
                form.errors or composer_notice or (ephemeral and ephemeral["kind"] == ERROR)
            ),
            "used": used,
            "limit": limit,
            "percent": percent,
            "tone": meter_tone(percent),
            "example": messages.EXAMPLE_QUESTION,
            "disclaimer": messages.DISCLAIMER,
        }
        return render(request, self.template_name, context)


class NewConversationView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request):
        request.session.pop(SESSION_KEY, None)
        return redirect("assistant:chat")
