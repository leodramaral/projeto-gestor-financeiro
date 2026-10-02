from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import base36_to_int


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    """Single-use, expiring token. Confirming the email changes the hash, which voids the link."""

    key_salt = "accounts.tokens.EmailConfirmationTokenGenerator"

    def _make_hash_value(self, user, timestamp):
        confirmed_at = user.email_confirmed_at.isoformat() if user.email_confirmed_at else ""
        return f"{user.pk}{user.email}{confirmed_at}{timestamp}"


class PasswordResetLinkTokenGenerator(PasswordResetTokenGenerator):
    """Password reset token: the hash covers the password, so changing it voids the link.

    Own salt, so it cannot stand in for a confirmation token (nor the reverse), and own lifetime,
    shorter than the one of the confirmation link.
    """

    key_salt = "accounts.tokens.PasswordResetLinkTokenGenerator"

    def check_token(self, user, token):
        # The parent validates the token against the (longer) PASSWORD_RESET_TIMEOUT; tighten it.
        if not super().check_token(user, token):
            return False
        issued_at = base36_to_int(token.split("-")[0])
        return self._num_seconds(self._now()) - issued_at <= settings.PASSWORD_RESET_LINK_TIMEOUT


email_confirmation_token = EmailConfirmationTokenGenerator()
password_reset_token = PasswordResetLinkTokenGenerator()
