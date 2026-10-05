from datetime import date
from decimal import Decimal

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

BEFORE = [("transactions", "0002_category")]
AFTER = [("transactions", "0005_category_icon")]


def migrate(targets):
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    executor.migrate(targets)
    return executor.loader.project_state(targets).apps


@pytest.fixture
def at_before_state(db):
    yield migrate(BEFORE)
    migrate(AFTER)


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_existing_expenses_move_to_other_and_incomes_stay_uncategorized(at_before_state):
    apps = at_before_state
    user_model = apps.get_model("accounts", "User")
    transaction_model = apps.get_model("transactions", "Transaction")
    user = user_model.objects.create(email="ana@exemplo.com", name="Ana")
    common = {"user": user, "amount": Decimal("12.50"), "date": date(2026, 9, 1)}
    expense = transaction_model.objects.create(kind="expense", description="Mercado", **common)
    income = transaction_model.objects.create(kind="income", description="Salário", **common)

    forward = migrate(AFTER)

    category_model = forward.get_model("transactions", "Category")
    transaction_model = forward.get_model("transactions", "Transaction")
    expense = transaction_model.objects.get(pk=expense.pk)
    income = transaction_model.objects.get(pk=income.pk)
    assert expense.category == category_model.objects.get(user=None, name="Outros")
    assert income.category is None
    assert (expense.amount, expense.date, expense.description) == (
        Decimal("12.50"),
        date(2026, 9, 1),
        "Mercado",
    )
    assert transaction_model.objects.count() == 2
    assert category_model.objects.filter(user=None).count() == 6


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_reversing_the_migration_removes_the_default_categories(at_before_state):
    apps = at_before_state

    assert apps.get_model("transactions", "Category").objects.count() == 0
    assert apps.get_model("transactions", "Transaction").objects.count() == 0


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_icon_migration_converts_emoji_to_icon_keys_and_back():
    before = migrate([("transactions", "0004_expense_requires_category")])
    category_model = before.get_model("transactions", "Category")
    user = before.get_model("accounts", "User").objects.create(email="ana@exemplo.com", name="Ana")
    mine = category_model.objects.create(user=user, name="Pets", emoji="🐶", color="amber")
    odd = category_model.objects.create(user=user, name="Estranha", emoji="🦄", color="blue")

    after = migrate([("transactions", "0005_category_icon")])

    category_model = after.get_model("transactions", "Category")
    icons = {c.name: c.icon for c in category_model.objects.all()}
    assert icons["Pets"] == "paw-print" and icons["Estranha"] == "package"
    assert icons["Alimentação"] == "utensils" and icons["Outros"] == "package"
    assert category_model.objects.get(pk=mine.pk).color == "amber"

    back = migrate([("transactions", "0004_expense_requires_category")])
    category_model = back.get_model("transactions", "Category")
    assert category_model.objects.get(pk=mine.pk).emoji == "🐶"
    assert category_model.objects.get(pk=odd.pk).emoji == "📦"
    assert category_model.objects.get(name="Alimentação").emoji == "🍔"
    migrate(AFTER)
