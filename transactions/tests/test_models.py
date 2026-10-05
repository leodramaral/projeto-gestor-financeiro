from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from transactions.models import Transaction, current_balance


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
