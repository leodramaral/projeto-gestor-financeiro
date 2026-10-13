from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction

from goals.models import Goal


@pytest.mark.parametrize(
    ("saved", "target", "expected"),
    [
        ("0.00", "500.00", 0),
        ("250.00", "500.00", 50),
        ("499.95", "500.00", 99),
        ("500.00", "500.00", 100),
        ("800.00", "500.00", 100),
    ],
)
def test_progress_percent_is_floored_and_capped(make_goal, user, saved, target, expected):
    goal = make_goal(user, target=target, saved=saved)
    assert goal.progress_percent == expected


def test_overdue_follows_the_deadline(make_goal, user, today):
    assert make_goal(user, deadline=today - timedelta(days=1)).is_overdue
    assert not make_goal(user, deadline=today).is_overdue
    assert not make_goal(user, deadline=today + timedelta(days=1)).is_overdue
    assert not make_goal(user, deadline=None).is_overdue


def test_completed_goal_is_never_overdue(make_goal, user, today):
    goal = make_goal(user, deadline=today - timedelta(days=5), completed=True)
    assert goal.is_completed
    assert not goal.is_overdue


def test_complete_and_reopen(make_goal, user):
    goal = make_goal(user)
    assert not goal.is_completed
    goal.complete()
    goal.refresh_from_db()
    assert goal.completed_at is not None
    goal.reopen()
    goal.refresh_from_db()
    assert goal.completed_at is None


def test_database_rejects_zero_target(user):
    with pytest.raises(IntegrityError), transaction.atomic():
        Goal.objects.create(user=user, name="x", target_amount=0)


def test_database_rejects_negative_saved(user):
    with pytest.raises(IntegrityError), transaction.atomic():
        Goal.objects.create(user=user, name="x", target_amount=10, saved_amount=-1)


def test_active_order_deadline_first_then_without_deadline(make_goal, user, today):
    late = make_goal(user, name="Depois", deadline=today + timedelta(days=40))
    none = make_goal(user, name="Sem prazo")
    soon = make_goal(user, name="Antes", deadline=today + timedelta(days=5))
    newer_none = make_goal(user, name="Sem prazo novo")
    assert list(Goal.objects.active()) == [soon, late, newer_none, none]


def test_completed_order_latest_first(make_goal, user):
    first = make_goal(user, name="Primeira", completed=True)
    second = make_goal(user, name="Segunda", completed=True)
    make_goal(user, name="Ativa")
    assert list(Goal.objects.completed()) == [second, first]


def test_str_is_the_name(make_goal, user):
    assert str(make_goal(user, name="Viagem")) == "Viagem"
