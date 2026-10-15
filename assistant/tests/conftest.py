from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from transactions.models import Category, Transaction

PASSWORD = "senha-segura-123"


@pytest.fixture(autouse=True)
def no_real_provider(monkeypatch):
    """A test that reaches the real provider would spend quota: make it fail instead."""

    def refuse(*args, **kwargs):
        raise AssertionError("A test tried to create the real LLM client; use a fake client.")

    monkeypatch.setattr("assistant.client.OpenAI", refuse)


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
def category(db):
    """A default category by name (seeded by the migrations)."""

    def get(name):
        return Category.objects.get(user__isnull=True, name=name)

    return get


@pytest.fixture
def make_expense(db):
    def make(user, category, amount="10.00", when=date(2026, 8, 10), description="Gasto"):
        return Transaction.objects.create(
            user=user,
            kind=Transaction.Kind.EXPENSE,
            amount=Decimal(amount),
            date=when,
            description=description,
            category=category,
        )

    return make


@pytest.fixture
def make_income(db):
    def make(user, amount="1000.00", when=date(2026, 8, 5)):
        return Transaction.objects.create(
            user=user,
            kind=Transaction.Kind.INCOME,
            amount=Decimal(amount),
            date=when,
            description="Salário",
        )

    return make


@pytest.fixture
def make_category(db):
    def make(user=None, name="Pets"):
        return Category.objects.create(user=user, name=name)

    return make
