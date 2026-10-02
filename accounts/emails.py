from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.emailing import send_templated_email

from .tokens import email_confirmation_token


def send_confirmation_email(user):
    """Email `user` a single-use link that confirms their address."""
    path = reverse(
        "accounts:confirm",
        kwargs={
            "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": email_confirmation_token.make_token(user),
        },
    )
    send_templated_email(
        user.email,
        "Confirme sua conta no Gestor Financeiro",
        "confirm_account",
        {
            "name": user.get_short_name(),
            "confirm_url": f"{settings.SITE_URL}{path}",
            "valid_days": settings.PASSWORD_RESET_TIMEOUT // 86400,
        },
    )
