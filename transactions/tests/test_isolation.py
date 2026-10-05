from decimal import Decimal

import pytest
from django.urls import reverse

from transactions.models import Transaction

pytestmark = pytest.mark.django_db

PAYLOAD = {"kind": "income", "amount": "999,00", "date": "2026-10-02", "description": "Invasor"}


@pytest.fixture
def foreign(other_user, make_transaction):
    """A transaction owned by someone other than the signed-in user."""
    return make_transaction(other_user, "expense", "42.00", description="Segredo da Bia")


def test_list_and_balances_only_show_own_data(logged_client, user, other_user, make_transaction):
    make_transaction(user, "income", "10.00", description="Meu")
    make_transaction(other_user, "income", "700.00", description="Da Bia")

    response = logged_client.get(reverse("transactions:list"))

    content = response.content.decode()
    assert [t.description for t in response.context["transactions"]] == ["Meu"]
    assert "Da Bia" not in content
    assert response.context["balance"] == Decimal("10.00")


def test_each_user_sees_only_their_own_list(client, user, other_user, make_transaction):
    make_transaction(user, description="Da Ana")
    make_transaction(other_user, description="Da Bia")

    client.force_login(other_user)
    mine = client.get(reverse("transactions:list")).context["transactions"]

    assert [t.description for t in mine] == ["Da Bia"]


@pytest.mark.parametrize("name", ["update", "delete"])
def test_get_of_foreign_transaction_is_404(logged_client, foreign, name):
    response = logged_client.get(reverse(f"transactions:{name}", args=[foreign.pk]))

    assert response.status_code == 404
    assert "Segredo da Bia" not in response.content.decode()


def test_edit_post_of_foreign_transaction_is_404_and_changes_nothing(logged_client, foreign):
    response = logged_client.post(reverse("transactions:update", args=[foreign.pk]), PAYLOAD)

    foreign.refresh_from_db()
    assert response.status_code == 404
    assert (foreign.kind, foreign.amount, foreign.description) == (
        "expense",
        Decimal("42.00"),
        "Segredo da Bia",
    )


def test_delete_post_of_foreign_transaction_is_404_and_keeps_it(logged_client, foreign):
    response = logged_client.post(reverse("transactions:delete", args=[foreign.pk]))

    assert response.status_code == 404
    assert Transaction.objects.filter(pk=foreign.pk).exists()


@pytest.mark.parametrize("name", ["update", "delete"])
@pytest.mark.parametrize("method", ["get", "post"])
def test_foreign_and_nonexistent_look_the_same(logged_client, foreign, name, method):
    call = getattr(logged_client, method)
    missing = Transaction.objects.order_by("-pk").first().pk + 1000

    foreign_response = call(reverse(f"transactions:{name}", args=[foreign.pk]))
    missing_response = call(reverse(f"transactions:{name}", args=[missing]))

    assert foreign_response.status_code == missing_response.status_code == 404
    assert foreign_response.content == missing_response.content


def test_creating_never_touches_other_users_data(logged_client, user, foreign):
    logged_client.post(reverse("transactions:create"), {**PAYLOAD, "user": foreign.user_id})

    assert Transaction.objects.filter(user=foreign.user).count() == 1
    assert Transaction.objects.get(description="Invasor").user == user
