from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from transactions.models import Category, Transaction

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
def make_transaction(db):
    def make(user, kind="expense", amount="10.00", when=None, description="Mercado", category=None):
        if kind == "expense" and category is None:
            category = Category.other()
        return Transaction.objects.create(
            user=user,
            kind=kind,
            amount=Decimal(amount),
            date=when or date(2026, 10, 1),
            description=description,
            category=category,
        )

    return make


@pytest.fixture
def make_category(db):
    def make(user=None, name="Pets", icon="paw-print", color="amber"):
        return Category.objects.create(user=user, name=name, icon=icon, color=color)

    return make


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client
