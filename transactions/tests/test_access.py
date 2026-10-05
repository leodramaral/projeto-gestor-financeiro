from urllib.parse import quote

import pytest
from django.test import Client
from django.urls import reverse

from transactions.models import Transaction

pytestmark = pytest.mark.django_db


@pytest.fixture
def item(user, make_transaction):
    return make_transaction(user, description="Original")


def routes(item):
    return [
        reverse("transactions:list"),
        reverse("transactions:create"),
        reverse("transactions:update", args=[item.pk]),
        reverse("transactions:delete", args=[item.pk]),
        reverse("home"),
    ]


@pytest.mark.parametrize("method", ["get", "post"])
def test_anonymous_is_redirected_to_login_on_every_route(client, item, method):
    for url in routes(item):
        response = getattr(client, method)(url)

        assert response.status_code == 302, url
        assert response.url.startswith(reverse("accounts:login")), url
        assert response.url == f"{reverse('accounts:login')}?next={quote(url)}", url


def test_anonymous_post_changes_nothing(client, item):
    for url in routes(item):
        client.post(
            url,
            {"kind": "income", "amount": "1", "date": "2026-10-01", "description": "Hack"},
        )

    item.refresh_from_db()
    assert item.description == "Original"
    assert Transaction.objects.count() == 1


def test_anonymous_sees_no_data_in_the_redirect(client, item):
    response = client.get(reverse("transactions:list"), follow=True)

    assert "Original" not in response.content.decode()


def test_post_without_csrf_token_is_rejected(user, item):
    strict = Client(enforce_csrf_checks=True)
    strict.force_login(user)
    data = {"kind": "income", "amount": "5", "date": "2026-10-01", "description": "Sem token"}

    assert strict.post(reverse("transactions:create"), data).status_code == 403
    assert strict.post(reverse("transactions:update", args=[item.pk]), data).status_code == 403
    assert strict.post(reverse("transactions:delete", args=[item.pk])).status_code == 403
    assert Transaction.objects.count() == 1
    assert Transaction.objects.get().description == "Original"
