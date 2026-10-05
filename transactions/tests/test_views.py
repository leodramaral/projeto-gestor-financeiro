import re
from datetime import date
from decimal import Decimal

import pytest
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from transactions.models import Transaction

pytestmark = pytest.mark.django_db

VALID = {"kind": "income", "amount": "150,50", "date": "2026-10-02", "description": "Salário"}


def checked_kinds(response):
    """Values of the kind radios that carry the `checked` attribute."""
    tags = re.findall(r"<input type=\"radio\"[^>]*>", response.content.decode())
    return [re.search(r'value="(\w+)"', tag).group(1) for tag in tags if " checked" in tag]


def current_page_marker(response):
    match = re.search(r'aria-current="page"[^>]*>(\d+)<', response.content.decode())
    return match.group(1) if match else None


def messages_of(response):
    return [str(m) for m in response.context["messages"]]


class TestList:
    def test_empty_state_and_zero_balance(self, logged_client):
        response = logged_client.get(reverse("transactions:list"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "ainda não tem lançamentos" in content
        assert "Registrar o primeiro lançamento" in content
        assert response.context["balance"] == Decimal("0.00")
        assert "R$ 0,00" in content

    def test_ordered_by_date_desc_then_newest_first(self, logged_client, user, make_transaction):
        old = make_transaction(user, when=date(2026, 9, 1))
        first = make_transaction(user, when=date(2026, 10, 1))
        second = make_transaction(user, when=date(2026, 10, 1))
        newest = make_transaction(user, when=date(2026, 10, 5))

        response = logged_client.get(reverse("transactions:list"))

        assert list(response.context["transactions"]) == [newest, second, first, old]

    def test_pagination_continues_the_order(self, logged_client, user, make_transaction):
        for day in range(45):
            make_transaction(user, when=date.fromordinal(date(2026, 1, 1).toordinal() + day))

        url = reverse("transactions:list")
        pages = [logged_client.get(url, {"page": n}) for n in (1, 2, 3)]

        sizes = [len(p.context["transactions"]) for p in pages]
        assert sizes == [20, 20, 5]
        dates = [t.date for p in pages for t in p.context["transactions"]]
        assert dates == sorted(dates, reverse=True)
        assert "?page=2" in pages[0].content.decode()
        assert current_page_marker(pages[1]) == "2"

    def test_nonexistent_page_is_404(self, logged_client, user, make_transaction):
        make_transaction(user)

        assert logged_client.get(reverse("transactions:list"), {"page": 2}).status_code == 404
        assert logged_client.get(reverse("transactions:list"), {"page": "abc"}).status_code == 404

    def test_balance_covers_all_pages_not_only_the_current_one(
        self, logged_client, user, make_transaction
    ):
        for _ in range(25):
            make_transaction(user, "income", "10.00")

        response = logged_client.get(reverse("transactions:list"))

        assert response.context["balance"] == Decimal("250.00")
        assert "R$ 250,00" in response.content.decode()

    def test_expense_and_income_are_visually_distinct(self, logged_client, user, make_transaction):
        make_transaction(user, "income", "5.00", description="Entrada X")
        make_transaction(user, "expense", "7.00", description="Despesa Y")

        content = logged_client.get(reverse("transactions:list")).content.decode()

        assert "+ R$ 5,00" in content
        assert "− R$ 7,00" in content
        assert "text-success-600" in content
        assert "text-error-500" in content


class TestTableUI:
    def test_row_shows_type_badge_icon_and_amount(self, logged_client, user, make_transaction):
        make_transaction(user, "income", "5.00", description="Entrada X")
        make_transaction(user, "expense", "7.00", description="Despesa Y")

        content = logged_client.get(reverse("transactions:list")).content.decode()

        assert content.count("rounded-full px-2 py-0.5") == 2
        assert content.count("h-10 w-10 shrink-0") == 2
        assert "Últimos lançamentos" in content
        assert "Entrada X" in content
        assert "Despesa Y" in content

    def test_row_menu_has_edit_and_delete_links_that_open_the_modal(
        self, logged_client, user, make_transaction
    ):
        item = make_transaction(user)

        content = logged_client.get(reverse("transactions:list")).content.decode()

        assert f'href="{reverse("transactions:update", args=[item.pk])}" data-modal' in content
        assert f'href="{reverse("transactions:delete", args=[item.pk])}" data-modal' in content
        assert 'role="menu"' in content
        assert 'aria-haspopup="menu"' in content

    def test_new_button_is_in_the_table_header(self, logged_client, user, make_transaction):
        make_transaction(user)

        content = logged_client.get(reverse("transactions:list")).content.decode()

        assert content.count(f'href="{reverse("transactions:create")}"') == 1

    def test_single_page_has_no_pagination_footer(self, logged_client, user, make_transaction):
        make_transaction(user)

        content = logged_client.get(reverse("transactions:list")).content.decode()

        assert 'aria-label="Paginação"' not in content

    def test_previous_is_disabled_on_the_first_page_and_next_on_the_last(
        self, logged_client, user, make_transaction
    ):
        for _ in range(45):
            make_transaction(user)
        url = reverse("transactions:list")

        first = logged_client.get(url).content.decode()
        middle = logged_client.get(url, {"page": 2}).content.decode()
        last = logged_client.get(url, {"page": 3}).content.decode()

        assert 'rel="prev"' not in first
        assert 'rel="next"' in first
        assert 'rel="prev"' in middle
        assert 'rel="next"' in middle
        assert 'rel="prev"' in last
        assert 'rel="next"' not in last
        assert first.count('aria-disabled="true"') == 1
        assert last.count('aria-disabled="true"') == 1

    def test_numbered_pages_mark_the_current_one(self, logged_client, user, make_transaction):
        for _ in range(45):
            make_transaction(user)

        response = logged_client.get(reverse("transactions:list"), {"page": 2})

        assert response.context["page_numbers"] == [1, 2, 3]
        assert current_page_marker(response) == "2"
        content = response.content.decode()
        assert 'href="?page=1"' in content
        assert 'href="?page=3"' in content

    def test_many_pages_are_elided_keeping_first_and_last(
        self, logged_client, user, make_transaction
    ):
        for _ in range(200):
            make_transaction(user)

        response = logged_client.get(reverse("transactions:list"), {"page": 5})

        numbers = response.context["page_numbers"]
        ellipsis = response.context["ellipsis"]
        assert numbers == [1, ellipsis, 4, 5, 6, ellipsis, 10]
        assert "…" in response.content.decode()


class TestCreate:
    def test_form_renders_with_today_as_default_date(self, logged_client):
        response = logged_client.get(reverse("transactions:create"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "csrfmiddlewaretoken" in content
        assert f'value="{timezone.localdate().isoformat()}"' in content

    def test_kind_renders_as_two_radio_buttons_with_none_checked(self, logged_client):
        response = logged_client.get(reverse("transactions:create"))
        content = response.content.decode()

        assert content.count('type="radio"') == 2
        assert 'value="income"' in content
        assert 'value="expense"' in content
        assert "Entrada" in content
        assert "Despesa" in content
        assert checked_kinds(response) == []
        assert "<select" not in content

    def test_missing_kind_shows_the_error_next_to_the_buttons(self, logged_client):
        response = logged_client.post(reverse("transactions:create"), {**VALID, "kind": ""})

        assert "Escolha o tipo do lançamento." in response.content.decode()
        assert not Transaction.objects.exists()

    def test_kind_stays_checked_after_an_invalid_post(self, logged_client):
        response = logged_client.post(
            reverse("transactions:create"), {**VALID, "kind": "expense", "amount": "0"}
        )

        assert checked_kinds(response) == ["expense"]

    def test_amount_field_carries_the_mask(self, logged_client):
        content = logged_client.get(reverse("transactions:create")).content.decode()

        assert "x-on:input=" in content
        assert "toLocaleString" in content

    def test_valid_post_creates_for_the_user(self, logged_client, user):
        response = logged_client.post(reverse("transactions:create"), VALID, follow=True)

        item = Transaction.objects.get()
        assert item.user == user
        assert item.amount == Decimal("150.50")
        assert item.kind == "income"
        assert item.date == date(2026, 10, 2)
        assert response.redirect_chain[-1][0] == reverse("transactions:list")
        assert "Lançamento registrado." in messages_of(response)

    def test_forged_user_field_is_ignored(self, logged_client, user, other_user):
        logged_client.post(reverse("transactions:create"), {**VALID, "user": other_user.pk})

        assert Transaction.objects.get().user == user

    def test_masked_amount_with_thousands_is_saved(self, logged_client):
        logged_client.post(reverse("transactions:create"), {**VALID, "amount": "1.234,56"})

        assert Transaction.objects.get().amount == Decimal("1234.56")

    @pytest.mark.parametrize("amount", ["0", "-3", "1,005", "abc"])
    def test_invalid_amount_creates_nothing(self, logged_client, amount):
        response = logged_client.post(reverse("transactions:create"), {**VALID, "amount": amount})

        assert response.status_code == 200
        assert response.context["form"].errors["amount"]
        assert not Transaction.objects.exists()

    def test_invalid_date_creates_nothing(self, logged_client):
        response = logged_client.post(
            reverse("transactions:create"), {**VALID, "date": "2026-02-31"}
        )

        assert response.status_code == 200
        assert "Informe uma data válida." in response.content.decode()
        assert not Transaction.objects.exists()

    def test_missing_fields_show_each_error(self, logged_client):
        response = logged_client.post(reverse("transactions:create"), {})

        errors = response.context["form"].errors
        assert set(errors) == {"kind", "amount", "date", "description"}
        assert not Transaction.objects.exists()


class TestUpdate:
    def test_form_is_prefilled(self, logged_client, user, make_transaction):
        item = make_transaction(user, description="Padaria")

        response = logged_client.get(reverse("transactions:update", args=[item.pk]))

        assert response.status_code == 200
        assert "Padaria" in response.content.decode()

    def test_form_shows_the_saved_kind_checked(self, logged_client, user, make_transaction):
        item = make_transaction(user, kind="income")

        response = logged_client.get(reverse("transactions:update", args=[item.pk]))

        assert checked_kinds(response) == ["income"]

    def test_valid_post_saves_and_keeps_owner(self, logged_client, user, make_transaction):
        item = make_transaction(user)

        response = logged_client.post(
            reverse("transactions:update", args=[item.pk]), VALID, follow=True
        )

        item.refresh_from_db()
        assert (item.kind, item.amount, item.description) == (
            "income",
            Decimal("150.50"),
            "Salário",
        )
        assert item.user == user
        assert "Lançamento atualizado." in messages_of(response)

    def test_invalid_post_keeps_the_transaction(self, logged_client, user, make_transaction):
        item = make_transaction(user, amount="10.00")

        response = logged_client.post(
            reverse("transactions:update", args=[item.pk]), {**VALID, "amount": "0"}
        )

        item.refresh_from_db()
        assert response.status_code == 200
        assert item.amount == Decimal("10.00")


class TestDelete:
    def test_get_shows_confirmation_and_does_not_delete(
        self, logged_client, user, make_transaction
    ):
        item = make_transaction(user, description="Aluguel")

        response = logged_client.get(reverse("transactions:delete", args=[item.pk]))

        assert response.status_code == 200
        content = response.content.decode()
        assert "Tem certeza" in content
        assert "Aluguel" in content
        assert Transaction.objects.filter(pk=item.pk).exists()

    def test_post_deletes(self, logged_client, user, make_transaction):
        item = make_transaction(user)

        response = logged_client.post(reverse("transactions:delete", args=[item.pk]), follow=True)

        assert not Transaction.objects.filter(pk=item.pk).exists()
        assert "Lançamento excluído." in messages_of(response)

    def test_cancel_link_goes_back_to_the_list(self, logged_client, user, make_transaction):
        item = make_transaction(user)

        content = logged_client.get(reverse("transactions:delete", args=[item.pk])).content.decode()

        assert f'href="{reverse("transactions:list")}"' in content


class TestNoInitialBalanceScreen:
    """The starting balance is an ordinary income: there is no separate screen for it."""

    def test_there_is_no_balance_route(self, logged_client):
        with pytest.raises(NoReverseMatch):
            reverse("transactions:balance")
        assert logged_client.get("/transactions/balance/").status_code == 404

    def test_list_does_not_offer_an_initial_balance_form(self, logged_client):
        content = logged_client.get(reverse("transactions:list")).content.decode()

        assert "Saldo inicial" not in content
        assert "alterar" not in content

    def test_starting_balance_registered_as_an_income_counts(self, logged_client, user):
        logged_client.post(
            reverse("transactions:create"),
            {**VALID, "amount": "1.500,00", "description": "Saldo inicial"},
        )

        response = logged_client.get(reverse("transactions:list"))

        assert response.context["balance"] == Decimal("1500.00")
        assert "R$ 1.500,00" in response.content.decode()


def test_every_screen_renders_inside_the_base_layout(logged_client, user, make_transaction):
    item = make_transaction(user)
    urls = [
        reverse("transactions:list"),
        reverse("transactions:create"),
        reverse("transactions:update", args=[item.pk]),
        reverse("transactions:delete", args=[item.pk]),
    ]

    for url in urls:
        response = logged_client.get(url)
        assert response.status_code == 200, url
        assert "base.html" in [t.name for t in response.templates], url
