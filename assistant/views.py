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


class ChatView(LoginRequiredMixin, View):
    """The conversation lives in the session: the last few messages, text only, and nothing else."""

    template_name = "assistant/chat.html"

    def get(self, request):
        return self._render(request, QuestionForm())

    def post(self, request):
        form = QuestionForm(request.POST)
        if not form.is_valid():
            return self._render(request, form)
        reservation = reserve_tokens(request.user, RESERVED_TOKENS, settings.LLM_DAILY_TOKEN_LIMIT)
        if reservation is None:
            return self._render(request, form, notice=messages.NO_CREDITS)
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
        if failure:
            logger.warning(
                "Assistant failure: cause=%s status=%s seconds=%.2f",
                failure.cause,
                failure.status,
                time.monotonic() - started,
            )
            return self._render(request, form, notice=failure.message, error=True)
        if result.outcome != TEXT:
            logger.info("Assistant declined: reason=%s tokens=%s", result.reason, result.tokens)
            return self._render(request, form, notice=result.text)
        history = [
            *history,
            {"role": "user", "content": question},
            {"role": "assistant", "content": result.text},
        ]
        request.session[SESSION_KEY] = history[-MAX_HISTORY_MESSAGES:]
        return redirect("assistant:chat")

    def _render(self, request, form, notice=None, error=False):
        if notice is None and not settings.LLM_API_KEY:
            notice, error = messages.UNAVAILABLE, True
        used = tokens_used_today(request.user)
        limit = settings.LLM_DAILY_TOKEN_LIMIT
        context = {
            "form": form,
            "conversation": request.session.get(SESSION_KEY, []),
            "notice": notice,
            "notice_is_error": error,
            "used": used,
            "limit": limit,
            "percent": min(100, used * 100 // limit) if limit else 100,
            "example": messages.EXAMPLE_QUESTION,
            "disclaimer": messages.DISCLAIMER,
        }
        return render(request, self.template_name, context)


class NewConversationView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request):
        request.session.pop(SESSION_KEY, None)
        return redirect("assistant:chat")
