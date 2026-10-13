from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from goals.models import Goal

PASSWORD = "senha-segura-123"


@pytest.fixture
def make_user(db):
    def make(email="ana@exemplo.com", name="Ana Souza"):
        return get_user_model().objects.create_user(email, PASSWORD, name=name)

    return make


@pytest.fixture
def user(make_user):
    return make_user()


@pytest.fixture
def other_user(make_user):
    return make_user("bia@exemplo.com", "Bia Lima")


@pytest.fixture
def logged(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def today():
    return timezone.localdate()


@pytest.fixture
def make_goal(db):
    def make(user, name="Reserva", target="500.00", saved="0.00", deadline=None, completed=False):
        goal = Goal.objects.create(
            user=user,
            name=name,
            target_amount=Decimal(target),
            saved_amount=Decimal(saved),
            deadline=deadline,
        )
        if completed:
            goal.complete()
        return goal

    return make


@pytest.fixture
def future(today):
    return today + timedelta(days=30)
