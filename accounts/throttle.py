"""Temporary lockout after repeated wrong-credential logins, keyed by normalized email."""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import LoginThrottle


def _normalize(email):
    return get_user_model().objects.normalize_email(email)


def lock_remaining(email):
    """Time left on the lock for `email` as a timedelta, or None when it is not locked."""
    locked_until = (
        LoginThrottle.objects.filter(email=_normalize(email))
        .values_list("locked_until", flat=True)
        .first()
    )
    if locked_until is None:
        return None
    remaining = locked_until - timezone.now()
    return remaining if remaining > timedelta(0) else None


def is_locked(email):
    return lock_remaining(email) is not None


def _ensure_row(email):
    try:
        with transaction.atomic():
            LoginThrottle.objects.get_or_create(email=email)
    except IntegrityError:  # a concurrent request created it first
        pass


def register_failure(email):
    """Count a wrong-credential attempt; lock the email when the limit is reached."""
    email = _normalize(email)
    with transaction.atomic():
        _ensure_row(email)
        throttle = LoginThrottle.objects.select_for_update().get(email=email)
        now = timezone.now()
        if throttle.locked_until is not None:
            if throttle.locked_until > now:
                # Already locked: a concurrent failure must not extend the lock.
                return
            # A lock that already ended starts a fresh count.
            throttle.locked_until = None
            throttle.failed_count = 0
        throttle.failed_count += 1
        if throttle.failed_count >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
            throttle.locked_until = now + timedelta(seconds=settings.LOGIN_LOCKOUT_SECONDS)
            throttle.failed_count = 0
        throttle.save()


def reset(email):
    """Forget the failures and lift any lock for `email`."""
    LoginThrottle.objects.filter(email=_normalize(email)).delete()
