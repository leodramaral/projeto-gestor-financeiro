from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    """Single-use, expiring token. Confirming the email changes the hash, which voids the link."""

    key_salt = "accounts.tokens.EmailConfirmationTokenGenerator"

    def _make_hash_value(self, user, timestamp):
        confirmed_at = user.email_confirmed_at.isoformat() if user.email_confirmed_at else ""
        return f"{user.pk}{user.email}{confirmed_at}{timestamp}"


email_confirmation_token = EmailConfirmationTokenGenerator()
