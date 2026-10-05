import json
from decimal import Decimal

import pytest
from django.urls import reverse

from transactions.models import Transaction

pytestmark = pytest.mark.django_db

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
VALID = {"kind": "income", "amount": "150,50", "date": "2026-10-02", "description": "Salário"}


@pytest.fixture
def item(user, make_transaction):
    return make_transaction(user, description="Padaria")


def screens(item):
    return [
        reverse("transactions:create"),
        reverse("transactions:update", args=[item.pk]),
        reverse("transactions:delete", args=[item.pk]),
    ]


def test_modal_request_gets_only_the_fragment(logged_client, item):
    for url in screens(item):
        response = logged_client.get(url, **AJAX)
        content = response.content.decode()

        assert response.status_code == 200, url
        assert "<html" not in content, url
        assert "sidebar" not in content, url
        assert "csrfmiddlewaretoken" in content, url
        assert "data-modal-close" in content, url


def test_plain_request_still_gets_the_full_page(logged_client, item):
    for url in screens(item):
        response = logged_client.get(url)

        assert "<html" in response.content.decode(), url
        assert "base.html" in [t.name for t in response.templates], url


def test_both_bodies_declare_vary(logged_client, item):
    for url in screens(item):
        for extra in ({}, AJAX):
            assert "X-Requested-With" in logged_client.get(url, **extra).headers["Vary"]


def test_modal_create_returns_json_location_and_queues_the_message(logged_client, user):
    response = logged_client.post(reverse("transactions:create"), VALID, **AJAX)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert json.loads(response.content) == {"location": reverse("transactions:list")}
    assert Transaction.objects.get().user == user
    page = logged_client.get(reverse("transactions:list"))
    assert "Lançamento registrado." in [str(m) for m in page.context["messages"]]


def test_modal_create_with_errors_returns_the_form_fragment(logged_client):
    response = logged_client.post(
        reverse("transactions:create"), {**VALID, "amount": "0", "kind": ""}, **AJAX
    )

    content = response.content.decode()
    assert response.status_code == 200
    assert "<html" not in content
    assert "O valor deve ser maior que zero." in content
    assert "Escolha o tipo do lançamento." in content
    assert not Transaction.objects.exists()


def test_modal_update_returns_json_and_saves(logged_client, item):
    response = logged_client.post(reverse("transactions:update", args=[item.pk]), VALID, **AJAX)

    item.refresh_from_db()
    assert json.loads(response.content) == {"location": reverse("transactions:list")}
    assert item.amount == Decimal("150.50")


def test_modal_update_with_errors_keeps_the_transaction(logged_client, item):
    response = logged_client.post(
        reverse("transactions:update", args=[item.pk]), {**VALID, "date": "2026-02-31"}, **AJAX
    )

    item.refresh_from_db()
    assert "Informe uma data válida." in response.content.decode()
    assert item.description == "Padaria"


def test_modal_delete_confirmation_does_not_delete_until_posted(logged_client, item):
    url = reverse("transactions:delete", args=[item.pk])

    logged_client.get(url, **AJAX)
    assert Transaction.objects.filter(pk=item.pk).exists()

    response = logged_client.post(url, **AJAX)

    assert json.loads(response.content) == {"location": reverse("transactions:list")}
    assert not Transaction.objects.filter(pk=item.pk).exists()


def test_modal_requests_for_foreign_transactions_are_404(
    logged_client, other_user, make_transaction
):
    foreign = make_transaction(other_user, description="Da Bia")

    for name in ("update", "delete"):
        url = reverse(f"transactions:{name}", args=[foreign.pk])
        assert logged_client.get(url, **AJAX).status_code == 404
        assert logged_client.post(url, VALID, **AJAX).status_code == 404
    foreign.refresh_from_db()
    assert foreign.description == "Da Bia"


def test_anonymous_modal_request_is_redirected_to_login(client, item):
    for url in screens(item):
        response = client.get(url, **AJAX)

        assert response.status_code == 302
        assert response.url.startswith(reverse("accounts:login"))


def test_list_links_open_in_the_modal_and_keep_real_urls(logged_client, item):
    content = logged_client.get(reverse("transactions:list")).content.decode()

    assert '<dialog id="transaction-modal"' in content
    assert "js/transaction-modal.js" in content
    for url in screens(item):
        assert f'href="{url}" data-modal' in content


def test_empty_list_offers_the_modal_too(logged_client):
    content = logged_client.get(reverse("transactions:list")).content.decode()

    assert f'href="{reverse("transactions:create")}" data-modal' in content


def test_modal_script_is_served_as_a_static_file(client):
    from django.contrib.staticfiles import finders

    assert finders.find("js/transaction-modal.js")
