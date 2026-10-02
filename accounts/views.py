import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.views.generic import FormView, TemplateView, View

from .emails import send_confirmation_email
from .forms import LoginForm, ResendConfirmationForm, SignupForm
from .tokens import email_confirmation_token

User = get_user_model()
logger = logging.getLogger(__name__)

SEND_FAILED_MESSAGE = "Não foi possível enviar o e-mail de confirmação. Tente novamente."


class AnonymousOnlyMixin:
    """Sends an already signed-in user to the dashboard."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)


class SignupView(AnonymousOnlyMixin, FormView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("accounts:signup_done")

    def form_valid(self, form):
        try:
            # The user is rolled back if the email cannot be sent: no account nobody can confirm.
            with transaction.atomic():
                user = form.save()
                send_confirmation_email(user)
        except (SMTPException, OSError):
            logger.exception("Could not send the confirmation email at signup")
            form.add_error(None, SEND_FAILED_MESSAGE)
            return self.form_invalid(form)
        return super().form_valid(form)


class SignupDoneView(AnonymousOnlyMixin, TemplateView):
    template_name = "accounts/signup_done.html"


class SignInView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data["remember_me"]:
            self.request.session.set_expiry(settings.SESSION_REMEMBER_SECONDS)
        else:
            self.request.session.set_expiry(0)
        return response


class ConfirmEmailView(View):
    """Confirms the account from the emailed link. Always renders a page, never a bare error."""

    def get(self, request, uidb64, token):
        user = self._get_user(uidb64)
        if user is None:
            return self._render(request, "invalid")
        if user.is_email_confirmed:
            return self._render(request, "already")
        if not email_confirmation_token.check_token(user, token):
            return self._render(request, "invalid")
        user.email_confirmed_at = timezone.now()
        user.save(update_fields=["email_confirmed_at"])
        return self._render(request, "confirmed")

    @staticmethod
    def _get_user(uidb64):
        try:
            return User.objects.get(pk=urlsafe_base64_decode(uidb64).decode())
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    @staticmethod
    def _render(request, outcome):
        return render(request, "accounts/confirm_result.html", {"outcome": outcome})


class ResendConfirmationView(AnonymousOnlyMixin, FormView):
    template_name = "accounts/resend_confirmation.html"
    form_class = ResendConfirmationForm
    success_url = reverse_lazy("accounts:resend_done")

    def get_initial(self):
        return {"email": self.request.GET.get("email", "")}

    def form_valid(self, form):
        user = User.objects.filter(
            email__iexact=form.cleaned_data["email"], is_active=True, email_confirmed_at=None
        ).first()
        if user is not None:
            try:
                send_confirmation_email(user)
            except (SMTPException, OSError):
                # The answer must not depend on the account existing, so a failure is only logged.
                logger.exception("Could not resend the confirmation email")
        return super().form_valid(form)


class ResendConfirmationDoneView(AnonymousOnlyMixin, TemplateView):
    template_name = "accounts/resend_confirmation_done.html"
