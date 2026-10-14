from datetime import date

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from assistant.models import Usage, add_tokens, tokens_used_today


@pytest.fixture
def freeze_day(monkeypatch):
    """Pins the local day the usage is counted in."""

    def freeze(day):
        monkeypatch.setattr(timezone, "localdate", lambda: day)

    return freeze


def test_a_user_without_usage_has_spent_nothing(user):
    assert tokens_used_today(user) == 0


def test_calls_on_the_same_day_are_summed(user):
    add_tokens(user, 900)
    add_tokens(user, 1300)

    assert tokens_used_today(user) == 2200
    assert Usage.objects.filter(user=user).count() == 1


def test_a_new_day_starts_at_zero(user, freeze_day):
    freeze_day(date(2026, 8, 10))
    add_tokens(user, 500)
    freeze_day(date(2026, 8, 11))

    assert tokens_used_today(user) == 0

    add_tokens(user, 70)
    assert tokens_used_today(user) == 70
    freeze_day(date(2026, 8, 10))
    assert tokens_used_today(user) == 500


def test_users_are_independent(user, other_user):
    add_tokens(user, 300)
    add_tokens(other_user, 40)

    assert tokens_used_today(user) == 300
    assert tokens_used_today(other_user) == 40


def test_zero_tokens_change_nothing(user):
    add_tokens(user, 0)

    assert not Usage.objects.exists()
    assert tokens_used_today(user) == 0


def test_there_is_one_row_per_user_and_day(user):
    Usage.objects.create(user=user, day=date(2026, 8, 10), tokens=1)

    with pytest.raises(IntegrityError), transaction.atomic():
        Usage.objects.create(user=user, day=date(2026, 8, 10), tokens=2)


def test_tokens_cannot_be_negative(user):
    with pytest.raises(IntegrityError), transaction.atomic():
        Usage.objects.create(user=user, day=date(2026, 8, 10), tokens=-1)


def test_usage_is_readable_in_the_admin_listing(user):
    usage = Usage.objects.create(user=user, day=date(2026, 8, 10), tokens=12)

    assert str(usage) == f"{user} 2026-08-10: 12"
