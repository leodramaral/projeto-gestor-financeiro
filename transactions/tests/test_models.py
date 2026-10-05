from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from transactions.models import Category, Transaction, current_balance


@pytest.mark.django_db
@pytest.mark.parametrize("amount", ["0.00", "-5.00"])
def test_database_rejects_non_positive_amount(user, amount):
    with pytest.raises(IntegrityError), transaction.atomic():
        Transaction.objects.create(
            user=user,
            kind="income",
            amount=Decimal(amount),
            date=date(2026, 10, 1),
            description="x",
        )


@pytest.mark.django_db
def test_deleting_user_removes_their_transactions(user, make_transaction):
    make_transaction(user)

    user.delete()

    assert not Transaction.objects.exists()


@pytest.mark.django_db
def test_default_ordering_is_newest_date_then_newest_id(user, make_transaction):
    old = make_transaction(user, when=date(2026, 9, 1))
    first = make_transaction(user, when=date(2026, 10, 1))
    second = make_transaction(user, when=date(2026, 10, 1))

    assert list(Transaction.objects.all()) == [second, first, old]


@pytest.mark.django_db
def test_str_representations(user, make_transaction):
    assert "Despesa" in str(make_transaction(user))


@pytest.mark.django_db
class TestCurrentBalance:
    def test_no_transactions_is_zero(self, user):
        assert current_balance(user) == Decimal("0.00")

    def test_only_incomes(self, user, make_transaction):
        make_transaction(user, "income", "100.00")
        make_transaction(user, "income", "50.50")

        assert current_balance(user) == Decimal("150.50")

    def test_only_expenses(self, user, make_transaction):
        make_transaction(user, "expense", "30.00")

        assert current_balance(user) == Decimal("-30.00")

    def test_mixed_incomes_and_expenses(self, user, make_transaction):
        make_transaction(user, "income", "200.00")
        make_transaction(user, "expense", "75.25")

        assert current_balance(user) == Decimal("124.75")

    def test_starting_balance_is_just_an_income(self, user, make_transaction):
        make_transaction(user, "income", "1000.00", description="Saldo inicial")
        make_transaction(user, "expense", "75.25")

        assert current_balance(user) == Decimal("924.75")

    def test_is_isolated_between_users(self, user, other_user, make_transaction):
        make_transaction(other_user, "income", "500.00")
        make_transaction(user, "income", "10.00")

        assert current_balance(user) == Decimal("10.00")
        assert current_balance(other_user) == Decimal("500.00")


@pytest.mark.django_db
def test_default_categories_exist_with_icon_and_color():
    defaults = {c.name: (c.icon, c.color) for c in Category.objects.filter(user__isnull=True)}

    assert defaults == {
        "Alimentação": ("utensils", "orange"),
        "Transporte": ("car", "blue"),
        "Moradia": ("house", "jade"),
        "Lazer": ("gamepad-2", "purple"),
        "Saúde": ("pill", "pink"),
        "Outros": ("package", "graphite"),
    }


@pytest.mark.django_db
@pytest.mark.parametrize("other_name", ["Pets", "pets", "PETS"])
def test_category_name_is_unique_per_user_ignoring_case(user, make_category, other_name):
    make_category(user, "Pets")

    with pytest.raises(IntegrityError), transaction.atomic():
        make_category(user, other_name)


@pytest.mark.django_db
def test_category_name_cannot_repeat_a_default_one(make_category):
    with pytest.raises(IntegrityError), transaction.atomic():
        make_category(None, "alimentação")


@pytest.mark.django_db
def test_two_users_can_have_the_same_category_name(user, other_user, make_category):
    make_category(user, "Pets")

    assert make_category(other_user, "Pets").pk


@pytest.mark.django_db
def test_for_user_returns_defaults_first_then_own_only(user, other_user, make_category):
    mine = make_category(user, "Pets")
    make_category(other_user, "Hobby")

    categories = list(Category.objects.for_user(user))

    assert categories[-1] == mine
    assert [c.user_id for c in categories[:-1]] == [None] * 6
    assert "Hobby" not in [c.name for c in categories]


@pytest.mark.django_db
def test_category_in_use_cannot_be_deleted_by_accident(user, make_category, make_transaction):
    pets = make_category(user, "Pets")
    make_transaction(user, category=pets)

    with pytest.raises(ProtectedError):
        pets.delete()


@pytest.mark.django_db
def test_database_rejects_an_expense_without_category(user):
    with pytest.raises(IntegrityError), transaction.atomic():
        Transaction.objects.create(
            user=user,
            kind="expense",
            amount=Decimal("5.00"),
            date=date(2026, 10, 1),
            description="x",
            category=None,
        )


@pytest.mark.django_db
def test_an_income_may_go_without_category(user, make_transaction):
    assert make_transaction(user, kind="income").category is None


@pytest.mark.django_db
def test_deleting_user_removes_their_categories(user, make_category):
    make_category(user, "Pets")

    user.delete()

    assert not Category.objects.filter(name="Pets").exists()
    assert Category.objects.filter(user__isnull=True).count() == 6


@pytest.mark.django_db
def test_category_is_shown_by_its_name(make_category):
    assert str(make_category(None, "Pets")) == "Pets"


@pytest.mark.django_db
def test_for_user_keeps_the_default_order_and_sorts_own_by_name(user, make_category):
    make_category(user, "zebra")
    make_category(user, "Abacate")

    names = [c.name for c in Category.objects.for_user(user)]

    assert names == [
        "Alimentação",
        "Transporte",
        "Moradia",
        "Lazer",
        "Saúde",
        "Outros",
        "Abacate",
        "zebra",
    ]
