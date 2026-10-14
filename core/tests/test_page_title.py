"""Every authenticated page has one h1 with its title and no breadcrumb trail."""

import re
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from goals.models import Goal
from transactions.models import Category, Transaction


@pytest.fixture
def logged_client(client, db):
    user = get_user_model().objects.create_user("ana@exemplo.com", "senha-segura-123", name="Ana")
    client.force_login(user)
    client.user = user
    return client


@pytest.fixture
def objects(logged_client):
    user = logged_client.user
    transaction = Transaction.objects.create(
        user=user,
        kind="expense",
        amount=Decimal("10.00"),
        date=date.today(),
        description="Mercado",
        category=Category.other(),
    )
    category = Category.objects.create(user=user, name="Pets", icon="paw-print", color="amber")
    goal = Goal.objects.create(user=user, name="Viagem", target_amount=Decimal("1000.00"))
    return {"transaction": transaction.pk, "category": category.pk, "goal": goal.pk}


# (url name, kwargs key into `objects` or None, expected h1)
PAGES = [
    ("home", None, "Painel"),
    ("dashboard_categories", None, "Painel"),
    ("dashboard_flow", None, "Painel"),
    ("dashboard_transactions", None, "Painel"),
    ("transactions:list", None, "Lançamentos"),
    ("transactions:create", None, "Novo lançamento"),
    ("transactions:update", "transaction", "Editar lançamento"),
    ("transactions:delete", "transaction", "Excluir lançamento"),
    ("transactions:category-list", None, "Categorias"),
    ("transactions:category-create", None, "Nova categoria"),
    ("transactions:category-update", "category", "Editar categoria"),
    ("transactions:category-delete", "category", "Excluir categoria"),
    ("goals:list", None, "Metas"),
    ("goals:create", None, "Nova meta"),
    ("goals:update", "goal", "Editar meta"),
    ("goals:progress", "goal", "Registrar progresso"),
    ("goals:delete", "goal", "Excluir meta"),
    ("accounts:profile", None, "Perfil"),
]


def get_page(client, objects, name, key):
    kwargs = {"pk": objects[key]} if key else {}
    return client.get(reverse(name, kwargs=kwargs))


@pytest.mark.django_db
@pytest.mark.parametrize(("name", "key", "title"), PAGES)
def test_page_has_a_single_h1_with_its_title(logged_client, objects, name, key, title):
    response = get_page(logged_client, objects, name, key)

    assert response.status_code == 200
    html = response.content.decode()
    headings = re.findall(r"<h1[^>]*>(.*?)</h1>", html, flags=re.S)
    assert [h.strip() for h in headings] == [title]


@pytest.mark.django_db
@pytest.mark.parametrize(("name", "key", "title"), PAGES)
def test_page_has_no_breadcrumb(logged_client, objects, name, key, title):
    html = get_page(logged_client, objects, name, key).content.decode()

    assert "Trilha de navegação" not in html


@pytest.mark.django_db
def test_modal_title_is_not_an_h1(logged_client):
    """The modal fragment keeps its h2: the page behind it owns the h1."""
    response = logged_client.get(
        reverse("transactions:create"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    html = response.content.decode()

    assert "<h2" in html
    assert "<h1" not in html
