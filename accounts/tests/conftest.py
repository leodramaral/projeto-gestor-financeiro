import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone

PASSWORD = "senha-segura-123"


@pytest.fixture
def make_user(db):
    def make(email="ana@exemplo.com", confirmed=True, **extra):
        user = get_user_model().objects.create_user(email, PASSWORD, name="Ana Souza", **extra)
        if confirmed:
            user.email_confirmed_at = timezone.now()
            user.save()
        return user

    return make


def confirmation_path(message=None):
    """Path of the confirmation link in the (last) email sent."""
    message = message or mail.outbox[-1]
    match = re.search(r"http://testserver(/accounts/confirm/[^\s<\"]+)", message.body)
    return match.group(1)
