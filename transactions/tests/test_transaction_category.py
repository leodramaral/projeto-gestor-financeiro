import pytest
from django.urls import reverse

from transactions.models import Category, Transaction

pytestmark = pytest.mark.django_db

EXPENSE = {"kind": "expense", "amount": "25,90", "date": "2026-10-02", "description": "Ração"}


def default(name):
    return Category.objects.get(user__isnull=True, name=name)


def test_create_expense_with_a_category(logged_client, user):
    response = logged_client.post(
        reverse("transactions:create"), {**EXPENSE, "category": default("Alimentação").pk}
    )

    assert response.status_code == 302
    assert Transaction.objects.get().category == default("Alimentação")


def test_create_expense_without_category_is_refused(logged_client):
    response = logged_client.post(reverse("transactions:create"), {**EXPENSE, "category": ""})

    assert response.status_code == 200
    assert "Escolha a categoria da despesa." in response.content.decode()
    assert not Transaction.objects.exists()


def test_create_income_ignores_a_forged_category(logged_client):
    response = logged_client.post(
        reverse("transactions:create"),
        {**EXPENSE, "kind": "income", "category": default("Lazer").pk},
    )

    assert response.status_code == 302
    assert Transaction.objects.get().category is None


def test_create_with_the_category_of_another_user_is_refused(
    logged_client, other_user, make_category
):
    theirs = make_category(other_user, "Hobby")

    response = logged_client.post(
        reverse("transactions:create"), {**EXPENSE, "category": theirs.pk}
    )

    assert response.status_code == 200
    assert "Escolha uma categoria da lista." in response.content.decode()
    assert not Transaction.objects.exists()


def test_edit_changes_the_category(logged_client, user, make_transaction, make_category):
    pets = make_category(user, "Pets")
    item = make_transaction(user)

    response = logged_client.post(
        reverse("transactions:update", args=[item.pk]), {**EXPENSE, "category": pets.pk}
    )

    assert response.status_code == 302
    item.refresh_from_db()
    assert item.category == pets


def test_switching_an_expense_to_income_clears_the_category(logged_client, user, make_transaction):
    item = make_transaction(user, category=default("Lazer"))

    logged_client.post(
        reverse("transactions:update", args=[item.pk]),
        {**EXPENSE, "kind": "income", "category": default("Lazer").pk},
    )

    item.refresh_from_db()
    assert item.kind == "income" and item.category is None


def test_switching_an_income_to_expense_requires_a_category(logged_client, user, make_transaction):
    item = make_transaction(user, kind="income")

    response = logged_client.post(
        reverse("transactions:update", args=[item.pk]), {**EXPENSE, "category": ""}
    )

    assert response.status_code == 200
    item.refresh_from_db()
    assert item.kind == "income"


def test_form_offers_defaults_and_own_categories_only(
    logged_client, user, other_user, make_category
):
    make_category(user, "Pets")
    make_category(other_user, "Hobby")

    content = logged_client.get(reverse("transactions:create")).content.decode()

    assert ">Alimentação</option>" in content and ">Pets</option>" in content
    assert "Hobby" not in content


def test_list_shows_icon_color_and_name_for_expenses_only(
    logged_client, user, make_transaction, make_category
):
    pets = make_category(user, "Pets", "paw-print", "amber")
    make_transaction(user, description="Ração", category=pets)
    make_transaction(user, kind="income", description="Salário")

    content = logged_client.get(reverse("transactions:list")).content.decode()

    assert "cat-amber" in content
    assert "Pets" in content
    assert content.count("cat-chip") == 1
    assert "lucide" not in content  # the icon is inline SVG, not a request


def test_list_uses_a_single_query_for_the_categories(
    logged_client, user, make_transaction, django_assert_max_num_queries
):
    for _ in range(5):
        make_transaction(user)

    with django_assert_max_num_queries(10):
        logged_client.get(reverse("transactions:list"))


class TestFilter:
    @pytest.fixture
    def lists(self, logged_client):
        def get(**params):
            return logged_client.get(reverse("transactions:list"), params)

        return get

    def test_filters_by_category_keeping_the_order(self, lists, user, make_transaction):
        from datetime import date

        lazer = default("Lazer")
        old = make_transaction(user, category=lazer, when=date(2026, 9, 1), description="Cinema")
        new = make_transaction(user, category=lazer, when=date(2026, 10, 1), description="Show")
        make_transaction(user, category=default("Moradia"), description="Aluguel")
        make_transaction(user, kind="income", description="Salário")

        response = lists(category=lazer.pk)

        assert list(response.context["transactions"]) == [new, old]
        assert response.context["selected_category"] == lazer

    def test_pagination_links_keep_the_filter(self, lists, user, make_transaction, settings):
        settings.TRANSACTIONS_PER_PAGE = 2
        lazer = default("Lazer")
        for _ in range(5):
            make_transaction(user, category=lazer)
        make_transaction(user, category=default("Moradia"))

        response = lists(category=lazer.pk)
        content = response.content.decode()

        assert f"?category={lazer.pk}&amp;page=2" in content  # `&` is escaped in the href
        assert "?page=" not in content
        page2 = lists(category=lazer.pk, page=3)
        assert len(page2.context["transactions"]) == 1

    def test_without_filter_links_have_no_category(self, lists, user, make_transaction, settings):
        settings.TRANSACTIONS_PER_PAGE = 1
        make_transaction(user)
        make_transaction(user)

        content = lists().content.decode()

        assert "?page=2" in content and "category=" not in content.split("<table")[1]

    def test_empty_filter_says_so_and_offers_to_clear(self, lists, user, make_transaction):
        make_transaction(user, category=default("Moradia"))

        content = lists(category=default("Lazer").pk).content.decode()

        assert "Nenhum lançamento na categoria Lazer." in content
        assert "Limpar o filtro" in content
        assert "ainda não tem lançamentos" not in content

    def test_balance_ignores_the_filter(self, lists, user, make_transaction):
        make_transaction(user, kind="income", amount="100.00")
        make_transaction(user, amount="30.00", category=default("Lazer"))

        assert lists().context["balance"] == lists(category=default("Lazer").pk).context["balance"]

    def test_select_marks_the_chosen_category(self, lists, user, make_transaction):
        make_transaction(user)
        lazer = default("Lazer")

        content = lists(category=lazer.pk).content.decode()

        assert f'<option value="{lazer.pk}" selected>' in content
        assert "Todas as categorias</option>" in content

    @pytest.mark.parametrize("raw", ["abc", "-1", "", "1.5", "99999999", "1 OR 1=1", "%"])
    def test_unusable_filter_is_ignored(self, lists, user, make_transaction, raw):
        mine = make_transaction(user)

        response = lists(category=raw)

        assert response.status_code == 200
        assert list(response.context["transactions"]) == [mine]
        assert response.context["selected_category"] is None

    def test_category_of_another_user_is_ignored(
        self, lists, user, other_user, make_category, make_transaction
    ):
        theirs = make_category(other_user, "Hobby")
        make_transaction(other_user, category=theirs, description="Segredo")
        mine = make_transaction(user)

        response = lists(category=theirs.pk)

        assert list(response.context["transactions"]) == [mine]
        assert "Segredo" not in response.content.decode()
        assert "Hobby" not in response.content.decode()

    def test_other_users_do_not_get_my_categories_in_the_filter(
        self, lists, user, other_user, make_category, make_transaction
    ):
        make_category(other_user, "Hobby")
        make_transaction(user)

        assert "Hobby" not in lists().content.decode()
