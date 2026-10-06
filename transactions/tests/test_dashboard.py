import json
from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from transactions.dashboard import build_dashboard, shift_month
from transactions.models import Category

pytestmark = pytest.mark.django_db

TODAY = date(2026, 10, 15)


def dec(value):
    return Decimal(value)


# --- window ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("day", "delta", "expected"),
    [
        (date(2026, 10, 31), -5, date(2026, 5, 1)),
        (date(2026, 1, 31), -1, date(2025, 12, 1)),
        (date(2026, 12, 15), 1, date(2027, 1, 1)),
        (date(2026, 3, 1), -14, date(2025, 1, 1)),
    ],
)
def test_shift_month_crosses_years(day, delta, expected):
    assert shift_month(day, delta) == expected


def test_window_has_six_months_in_order_with_gaps_filled(user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 8, 3))
    make_transaction(user, "expense", "30.00", when=date(2026, 10, 2))

    months = build_dashboard(user, TODAY).months

    assert [m.label for m in months] == ["mai", "jun", "jul", "ago", "set", "out"]
    assert [m.income for m in months] == [0, 0, 0, 100, 0, 0]
    assert [m.expense for m in months] == [0, 0, 0, 0, 0, 30]
    assert [m.balance for m in months] == [0, 0, 0, 100, 100, 70]


def test_window_across_the_year_boundary(user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2025, 12, 10))

    months = build_dashboard(user, date(2026, 1, 31)).months

    assert [m.label for m in months] == ["ago", "set", "out", "nov", "dez", "jan"]
    assert months[4].income == dec("10.00")


def test_balance_starts_from_everything_before_the_window(user, make_transaction):
    make_transaction(user, "income", "1000.00", when=date(2025, 1, 10))
    make_transaction(user, "expense", "250.00", when=date(2026, 4, 30))
    make_transaction(user, "income", "50.00", when=date(2026, 5, 1))

    months = build_dashboard(user, TODAY).months

    assert months[0].balance == dec("800.00")
    assert months[-1].balance == dec("800.00")


def test_future_transactions_stay_out_of_the_charts(user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 5))
    make_transaction(user, "income", "999.00", when=date(2026, 11, 2))

    dashboard = build_dashboard(user, TODAY)

    assert dashboard.months[-1].income == dec("100.00")
    assert dashboard.months[-1].balance == dec("100.00")
    # The card uses every transaction, like the list does.
    assert dashboard.balance == dec("1099.00")


def test_last_point_matches_the_balance(user, make_transaction):
    make_transaction(user, "income", "500.00", when=date(2025, 6, 1))
    make_transaction(user, "expense", "120.50", when=date(2026, 9, 9))
    make_transaction(user, "income", "70.00", when=date(2026, 10, 9))

    dashboard = build_dashboard(user, TODAY)

    assert dashboard.months[-1].balance == dashboard.balance == dec("449.50")


# --- month cards ----------------------------------------------------------------------------


def test_month_totals_ignore_other_months(user, make_transaction):
    make_transaction(user, "income", "300.00", when=date(2026, 10, 1))
    make_transaction(user, "expense", "100.00", when=date(2026, 10, 31))
    make_transaction(user, "expense", "999.00", when=date(2026, 9, 30))

    dashboard = build_dashboard(user, TODAY)

    assert dashboard.month_income == dec("300.00")
    assert dashboard.month_expense == dec("100.00")
    assert dashboard.savings_rate == dec("66.7")


def test_change_against_the_previous_month(user, make_transaction):
    make_transaction(user, "expense", "100.00", when=date(2026, 9, 10))
    make_transaction(user, "expense", "150.00", when=date(2026, 10, 10))
    make_transaction(user, "income", "200.00", when=date(2026, 9, 10))
    make_transaction(user, "income", "100.00", when=date(2026, 10, 10))

    dashboard = build_dashboard(user, TODAY)

    assert dashboard.expense_change == 50
    assert dashboard.income_change == -50


def test_no_change_without_a_base(user, make_transaction):
    make_transaction(user, "income", "200.00", when=date(2026, 10, 10))

    dashboard = build_dashboard(user, TODAY)

    assert dashboard.income_change is None
    assert dashboard.expense_change is None


def test_savings_rate_is_unavailable_without_income(user, make_transaction):
    make_transaction(user, "expense", "80.00", when=date(2026, 10, 10))

    assert build_dashboard(user, TODAY).savings_rate is None


# --- categories -----------------------------------------------------------------------------


def test_slices_group_expenses_by_category_and_match_the_totals(
    user, make_transaction, make_category
):
    food = make_category(user, "Mercado", color="green")
    pets = make_category(user, "Pets", color="amber")
    make_transaction(user, "expense", "60.00", when=date(2026, 10, 3), category=food)
    make_transaction(user, "expense", "40.00", when=date(2026, 10, 4), category=food)
    make_transaction(user, "expense", "100.00", when=date(2026, 10, 5), category=pets)
    make_transaction(user, "income", "500.00", when=date(2026, 10, 6))
    make_transaction(user, "expense", "70.00", when=date(2026, 9, 6), category=pets)

    dashboard = build_dashboard(user, TODAY)

    assert [(s.name, s.amount, s.percent) for s in dashboard.categories] == [
        ("Mercado", dec("100.00"), 50),
        ("Pets", dec("100.00"), 50),
    ]
    assert sum(s.amount for s in dashboard.categories) == dashboard.month_expense


def test_slice_matches_the_filtered_list(logged_client, user, make_transaction, make_category):
    food = make_category(user, "Mercado")
    make_transaction(user, "expense", "12.34", when=date(2026, 10, 3), category=food)
    make_transaction(user, "expense", "7.66", when=date(2026, 10, 9), category=food)
    make_transaction(user, "expense", "5.00", when=date(2026, 10, 9))

    slice_ = build_dashboard(user, TODAY).categories
    listed = logged_client.get(reverse("transactions:list"), {"category": food.pk}).context[
        "transactions"
    ]

    amount = next(s.amount for s in slice_ if s.name == "Mercado")
    assert amount == sum(t.amount for t in listed) == dec("20.00")


def test_only_the_five_largest_categories_get_a_slice(user, make_transaction, make_category):
    for index in range(7):
        category = make_category(user, f"Cat {index}", color="blue")
        make_transaction(
            user, "expense", f"{10 * (index + 1)}.00", when=date(2026, 10, 2), category=category
        )

    slices = build_dashboard(user, TODAY).categories

    assert [s.name for s in slices] == ["Cat 6", "Cat 5", "Cat 4", "Cat 3", "Cat 2", "Outras"]
    assert slices[-1].amount == dec("30.00")
    assert slices[-1].color == "graphite"


def test_no_slices_without_expenses_in_the_month(user, make_transaction):
    make_transaction(user, "income", "50.00", when=date(2026, 10, 2))
    make_transaction(user, "expense", "20.00", when=date(2026, 9, 2))

    assert build_dashboard(user, TODAY).categories == []


def test_slice_with_an_unknown_color_falls_back_to_the_default(
    user, make_transaction, make_category
):
    odd = make_category(user, "Estranha")
    Category.objects.filter(pk=odd.pk).update(color="nao-existe")
    make_transaction(user, "expense", "10.00", when=date(2026, 10, 2), category=odd)

    assert build_dashboard(user, TODAY).categories[0].color == "graphite"


# --- recent ---------------------------------------------------------------------------------


def test_recent_are_the_five_newest_in_list_order(user, make_transaction):
    for day in range(1, 8):
        make_transaction(user, "income", "1.00", when=date(2026, 10, day), description=f"d{day}")

    recent = build_dashboard(user, TODAY).recent

    assert [t.description for t in recent] == ["d7", "d6", "d5", "d4", "d3"]


# --- isolation ------------------------------------------------------------------------------


def test_nothing_of_another_user_leaks_into_the_numbers(
    user, other_user, make_transaction, make_category
):
    secret = make_category(other_user, "Segredo da Bia")
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2), description="Meu")
    make_transaction(other_user, "income", "700.00", when=date(2026, 9, 2), description="Da Bia")
    make_transaction(other_user, "expense", "55.00", when=date(2026, 10, 2), category=secret)

    dashboard = build_dashboard(user, TODAY)

    assert dashboard.balance == dec("10.00")
    assert dashboard.month_income == dec("10.00")
    assert dashboard.month_expense == 0
    assert dashboard.categories == []
    assert [m.income for m in dashboard.months] == [0, 0, 0, 0, 0, 10]
    assert [t.description for t in dashboard.recent] == ["Meu"]


# --- the page -------------------------------------------------------------------------------


def test_home_requires_login(client):
    response = client.get(reverse("home"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


def test_home_renders_the_dashboard_with_the_sidebar_item(logged_client):
    response = logged_client.get(reverse("home"))

    assert response.status_code == 200
    assert "core/home.html" in [t.name for t in response.templates]
    content = response.content.decode()
    assert "<h2" in content and "Painel" in content
    assert content.count('aria-current="page"') >= 1
    assert 'href="/" class="menu-item group menu-item-active"' in content


def test_empty_account_shows_the_invitation_and_no_charts(logged_client):
    response = logged_client.get(reverse("home"))

    content = response.content.decode()
    assert response.status_code == 200
    assert "Nenhum lançamento ainda" in content
    assert reverse("transactions:create") in content
    assert "R$ 0,00" in content
    assert "dashboard-data" not in content
    assert "chart.umd.min.js" not in content
    assert "chart-balance" not in content


def test_negative_balance_is_red_with_the_warning(logged_client, user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 1))
    make_transaction(user, "expense", "512.30", when=date(2026, 10, 2))

    content = logged_client.get(reverse("home")).content.decode()

    assert "Você está no vermelho, cuidado" in content
    assert "text-error-500" in content.split("data-balance>")[0].rsplit("<p", 1)[1]
    assert "Você está no verde" not in content


def test_zero_balance_has_no_status_message(logged_client, user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 1))
    make_transaction(user, "expense", "100.00", when=date(2026, 10, 2))

    content = logged_client.get(reverse("home")).content.decode()

    assert "data-balance-status" not in content
    assert "no vermelho" not in content
    assert "no verde" not in content


def test_positive_balance_has_the_motivational_message(logged_client, user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 1))

    content = logged_client.get(reverse("home")).content.decode()

    assert "Você está no verde. Continue assim!" in content
    assert "no vermelho" not in content


def test_dashboard_balance_equals_the_list_balance(logged_client, user, make_transaction):
    make_transaction(user, "income", "1234.56", when=date(2025, 3, 1))
    make_transaction(user, "expense", "34.06", when=date(2026, 9, 1))

    home = logged_client.get(reverse("home")).context["dashboard"].balance
    listed = logged_client.get(reverse("transactions:list")).context["balance"]

    assert home == listed == dec("1200.50")


def test_page_reflects_create_edit_and_delete_right_away(logged_client, user, make_transaction):
    first = make_transaction(user, "income", "100.00")
    assert "R$ 100,00" in logged_client.get(reverse("home")).content.decode()

    logged_client.post(
        reverse("transactions:update", args=[first.pk]),
        {"kind": "income", "amount": "250,00", "date": "2026-10-01", "description": "Salário"},
    )
    assert "R$ 250,00" in logged_client.get(reverse("home")).content.decode()

    logged_client.post(reverse("transactions:delete", args=[first.pk]))
    assert "Nenhum lançamento ainda" in logged_client.get(reverse("home")).content.decode()


def test_month_without_expenses_shows_the_message_instead_of_the_donut(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "100.00", when=timezone.localdate())

    content = logged_client.get(reverse("home")).content.decode()

    assert "Nenhum gasto registrado neste mês." in content
    assert 'id="chart-categories"' not in content
    assert 'id="chart-cashflow"' in content


def test_month_without_income_shows_the_unavailable_savings_rate(
    logged_client, user, make_transaction
):
    make_transaction(user, "expense", "30.00", when=timezone.localdate())

    content = logged_client.get(reverse("home")).content.decode()

    assert "Sem entradas neste mês" in content
    assert "data-income-change" not in content


def test_chart_data_is_embedded_as_json_and_escaped(
    logged_client, user, make_transaction, make_category
):
    evil = make_category(user, "</script><b>x", color="blue")
    make_transaction(user, "expense", "10.00", when=timezone.localdate(), category=evil)

    content = logged_client.get(reverse("home")).content.decode()

    assert "</script><b>x" not in content
    payload = content.split('id="dashboard-data" type="application/json">')[1].split("</script>")[0]
    data = json.loads(payload)
    assert data["categories"][0]["name"] == "</script><b>x"
    assert data["categories"][0]["amount"] == 10.0
    assert len(data["months"]) == len(data["balance"]) == 6


def test_page_loads_scripts_locally_only(logged_client, user, make_transaction):
    make_transaction(user, "income", "1.00")

    content = logged_client.get(reverse("home")).content.decode()

    assert "dist/js/chart.umd.min.js" in content
    assert "js/dashboard-charts.js" in content
    assert "https://" not in "".join(
        line for line in content.splitlines() if "<script" in line and "src=" in line
    )


def test_recent_list_links_to_the_full_list(logged_client, user, make_transaction):
    make_transaction(user, "income", "1.00", description="Salário")

    content = logged_client.get(reverse("home")).content.decode()

    assert "Salário" in content
    assert f'href="{reverse("transactions:list")}"' in content


def test_page_only_shows_the_users_own_data(
    logged_client, user, other_user, make_transaction, make_category
):
    secret = make_category(other_user, "Segredo da Bia")
    make_transaction(user, "income", "10.00", description="Meu")
    make_transaction(other_user, "expense", "55.00", description="Da Bia", category=secret)

    content = logged_client.get(reverse("home")).content.decode()

    assert "Da Bia" not in content
    assert "Segredo da Bia" not in content
