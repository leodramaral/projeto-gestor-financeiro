import json
import re
from datetime import date

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

TODAY = date(2026, 10, 15)
TAB_ROUTES = ["home", "dashboard_categories", "dashboard_flow", "dashboard_transactions"]


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch):
    monkeypatch.setattr("django.utils.timezone.localdate", lambda *a, **k: TODAY)


def page(client, route="home", **params):
    return client.get(reverse(route), params)


def html(client, route="home", **params):
    return page(client, route, **params).content.decode()


def embedded_data(content):
    """The chart data the page embeds with `json_script`, decoded."""
    payload = content.split('id="dashboard-data" type="application/json">')[1]
    return json.loads(payload.split("</script>")[0])


def text_of(fragment):
    """The visible text of an HTML fragment, with the whitespace collapsed."""
    return " ".join(re.sub(r"<[^>]+>", " ", fragment).split())


def known_october(user, make_transaction):
    """A month with known numbers: opening R$ 1.250,00, lowest on the 4th, closing R$ 4.425,35."""
    make_transaction(user, "income", "1250.00", when=date(2026, 9, 20))
    make_transaction(user, "expense", "1500.00", when=date(2026, 10, 2))
    make_transaction(user, "expense", "745.80", when=date(2026, 10, 3))
    make_transaction(user, "expense", "212.35", when=date(2026, 10, 4))
    make_transaction(user, "income", "5600.00", when=date(2026, 10, 5))
    make_transaction(user, "income", "100.00", when=date(2026, 10, 15))
    make_transaction(user, "expense", "66.50", when=date(2026, 10, 31))


# Day by day of `known_october` (index 0 is the 1st).
KNOWN_INCOME = [0.0] * 4 + [5600.0] + [0.0] * 9 + [100.0] + [0.0] * 16
KNOWN_EXPENSE = [0.0, 1500.0, 745.8, 212.35] + [0.0] * 26 + [66.5]
KNOWN_BALANCE = [1250.0, -250.0, -995.8, -1208.15] + [4391.85] * 10 + [4491.85] * 16 + [4425.35]


# --- access and layout ----------------------------------------------------------------------


@pytest.mark.parametrize("route", TAB_ROUTES)
def test_every_tab_requires_login(client, route):
    response = client.get(reverse(route))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.parametrize("route", TAB_ROUTES)
def test_every_tab_renders_and_marks_the_sidebar_item(logged_client, user, make_transaction, route):
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2))

    response = page(logged_client, route)
    content = response.content.decode()

    assert response.status_code == 200
    assert 'href="/" class="menu-item group menu-item-active" aria-current="page"' in content


def test_home_is_the_overview_template(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2))

    templates = [t.name for t in page(logged_client).templates]

    assert "core/home.html" in templates
    assert reverse("home") == "/"


# --- empty state ----------------------------------------------------------------------------


@pytest.mark.parametrize("route", TAB_ROUTES)
def test_empty_account_shows_the_invitation_and_nothing_else(logged_client, route):
    response = page(logged_client, route)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Nenhum lançamento ainda" in content
    assert reverse("transactions:create") in content
    assert "R$ 0,00" in content
    for absent in ("data-month-selector", "data-dashboard-tabs", "dashboard-data"):
        assert absent not in content
    assert "chart.umd.min.js" not in content
    assert "chart-balance" not in content


def test_empty_month_of_a_user_with_history_is_not_the_empty_state(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "100.00", when=date(2026, 8, 10))

    content = html(logged_client, month="2026-10")

    assert "Nenhum lançamento ainda" not in content
    assert "data-month-selector" in content and "data-dashboard-tabs" in content
    summary = logged_client.get(reverse("home")).context["dashboard"].summary
    assert (summary.income, summary.expense) == (0, 0)
    assert summary.opening == summary.closing == 100
    assert "Nenhum gasto registrado neste mês." in content


# --- month selector -------------------------------------------------------------------------


def test_default_month_is_the_current_one(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 8, 2))

    response = page(logged_client)

    assert response.context["month"].param == "2026-10"
    assert "outubro de 2026" in response.content.decode().lower()


def test_selector_links_carry_the_neighbour_months(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 6, 2))

    content = html(logged_client, month="2026-08")

    assert f'href="{reverse("home")}?month=2026-07"' in content
    assert f'href="{reverse("home")}?month=2026-09"' in content
    assert "agosto de 2026" in content.lower()


def test_next_arrow_is_disabled_on_the_current_month(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 6, 2))

    response = page(logged_client)
    content = response.content.decode()

    assert response.context["next_url"] is None
    assert 'aria-disabled="true" aria-label="Próximo mês"' in content
    assert 'aria-label="Mês anterior" data-month-previous' in content  # still a link


def test_previous_arrow_is_disabled_on_the_first_transaction_month(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "10.00", when=date(2026, 8, 20))

    response = page(logged_client, month="2026-08")

    assert response.context["previous_url"] is None
    assert 'aria-disabled="true" aria-label="Mês anterior"' in response.content.decode()
    assert page(logged_client, month="2026-09").context["previous_url"].endswith("month=2026-08")


@pytest.mark.parametrize(
    "raw", ["2026-13", "0001-01", "abc", "", "2027-01", "2026-11", "2026-10-05"]
)
def test_invalid_or_future_month_falls_back_to_the_current_one(
    logged_client, user, make_transaction, raw
):
    make_transaction(user, "income", "10.00", when=date(2026, 8, 2))

    response = page(logged_client, month=raw)

    assert response.status_code == 200
    assert response.context["month"].param == "2026-10"


def test_a_month_before_2025_with_transactions_is_shown(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2024, 12, 5))

    response = page(logged_client, month="2024-12")

    assert response.context["month"].param == "2024-12"


@pytest.mark.parametrize("route", TAB_ROUTES)
def test_the_chosen_month_survives_every_tab_link(logged_client, user, make_transaction, route):
    make_transaction(user, "income", "10.00", when=date(2026, 7, 2))

    tabs = page(logged_client, route, month="2026-08").context["tabs"]

    assert [t["url"] for t in tabs] == [f"{reverse(name)}?month=2026-08" for name in TAB_ROUTES]
    assert [t["active"] for t in tabs] == [name == route for name in TAB_ROUTES]


@pytest.mark.parametrize("route", TAB_ROUTES)
def test_every_tab_shows_the_same_month_and_the_same_transactions(
    logged_client, user, make_transaction, route
):
    make_transaction(user, "income", "10.00", when=date(2026, 8, 5), description="de agosto")
    make_transaction(user, "income", "10.00", when=date(2026, 9, 5), description="de setembro")

    response = page(logged_client, route, month="2026-08")

    assert response.context["month"].param == "2026-08"
    assert "agosto de 2026" in response.content.decode()
    assert "de setembro" not in response.content.decode()


# --- overview -------------------------------------------------------------------------------


def test_overview_has_every_chart_and_a_link_to_each_segment(
    logged_client, user, make_transaction, make_category
):
    food = make_category(user, "Mercado")
    make_transaction(user, "expense", "30.00", when=date(2026, 9, 3), category=food)

    response = page(logged_client, month="2026-09")
    content = response.content.decode()

    for canvas in ("chart-cashflow", "chart-balance", "chart-categories"):
        assert f'id="{canvas}"' in content
    tabs = {t["key"]: t["url"] for t in response.context["tabs"]}
    for key in ("categories", "flow", "transactions"):
        assert f'href="{tabs[key]}"' in content
    assert tabs["categories"] == f"{reverse('dashboard_categories')}?month=2026-09"
    assert "month=2026-09" in tabs["transactions"]


def test_overview_recent_list_is_the_months_five_newest(logged_client, user, make_transaction):
    for day in range(1, 8):
        make_transaction(user, "income", "1.00", when=date(2026, 10, day), description=f"dia{day}")
    make_transaction(user, "income", "1.00", when=date(2026, 9, 30), description="mês passado")

    content = html(logged_client)

    assert all(f"dia{day}" in content for day in range(3, 8))
    assert "dia2" not in content and "mês passado" not in content


# --- balance of the month -------------------------------------------------------------------


def test_negative_balance_is_red_with_the_warning(logged_client, user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 1))
    make_transaction(user, "expense", "512.30", when=date(2026, 10, 2))

    content = html(logged_client)

    assert "Você está no vermelho, cuidado" in content
    assert "text-error-600" in content.split("data-balance>")[0].rsplit("<p", 1)[1]
    assert "− R$ 412,30" in content
    assert "Você está no verde" not in content


def test_zero_balance_has_no_status_message(logged_client, user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 1))
    make_transaction(user, "expense", "100.00", when=date(2026, 10, 2))

    content = html(logged_client)

    assert "data-balance-status" not in content
    assert "no vermelho" not in content and "no verde" not in content


def test_positive_balance_has_the_motivational_message(logged_client, user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 1))

    content = html(logged_client)

    assert "Você está no verde. Continue assim!" in content
    assert "no vermelho" not in content


def test_status_follows_the_chosen_month(logged_client, user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 8, 1))
    make_transaction(user, "expense", "150.00", when=date(2026, 9, 1))

    assert "no verde" in html(logged_client, month="2026-08")
    assert "no vermelho" in html(logged_client, month="2026-09")


def test_opening_and_closing_balance_are_shown(logged_client, user, make_transaction):
    make_transaction(user, "income", "1000.00", when=date(2026, 9, 1))
    make_transaction(user, "income", "200.00", when=date(2026, 10, 1))
    make_transaction(user, "expense", "50.00", when=date(2026, 10, 2))

    content = html(logged_client)

    assert "R$ 1.000,00" in content.split("data-opening>")[1].split("</p>")[0]
    assert "R$ 1.150,00" in content.split("data-balance>")[1].split("</p>")[0]


def test_closing_balance_equals_the_list_balance(logged_client, user, make_transaction):
    make_transaction(user, "income", "1234.56", when=date(2025, 3, 1))
    make_transaction(user, "expense", "34.06", when=date(2026, 9, 1))

    closing = page(logged_client).context["dashboard"].summary.closing
    listed = logged_client.get(reverse("transactions:list")).context["balance"]

    assert closing == listed


def test_page_reflects_create_edit_and_delete_right_away(logged_client, user, make_transaction):
    first = make_transaction(user, "income", "100.00", when=date(2026, 10, 1))
    assert "R$ 100,00" in html(logged_client)

    logged_client.post(
        reverse("transactions:update", args=[first.pk]),
        {"kind": "income", "amount": "250,00", "date": "2026-10-01", "description": "Salário"},
    )
    assert "R$ 250,00" in html(logged_client)

    logged_client.post(reverse("transactions:delete", args=[first.pk]))
    assert "Nenhum lançamento ainda" in html(logged_client)


# --- cards ----------------------------------------------------------------------------------


def test_month_without_expenses_shows_the_message_instead_of_the_donut(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 3))

    content = html(logged_client)

    assert "Nenhum gasto registrado neste mês." in content
    assert 'id="chart-categories"' not in content
    assert 'id="chart-cashflow"' in content


def test_month_without_income_shows_the_unavailable_savings_rate(
    logged_client, user, make_transaction
):
    make_transaction(user, "expense", "30.00", when=date(2026, 10, 3))

    content = html(logged_client)

    assert "Sem entradas neste mês" in content
    assert "data-income-change" not in content
    assert "sem divisão por zero" in content


def test_cards_show_no_base_when_the_previous_month_has_no_movement(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 3))
    make_transaction(user, "expense", "30.00", when=date(2026, 10, 4))

    content = html(logged_client)

    assert "data-income-no-base" in content
    assert "data-expense-no-base" in content
    assert "data-income-change" not in content
    assert "data-expense-change" not in content


def test_cards_show_the_change_against_the_previous_month(logged_client, user, make_transaction):
    make_transaction(user, "expense", "100.00", when=date(2026, 9, 3))
    make_transaction(user, "expense", "150.00", when=date(2026, 10, 3))

    content = html(logged_client)

    assert "▲ 50%" in content.split("data-expense-change>")[1].split("</span>")[0] + "%"
    assert "em relação ao mês anterior" in content


# --- card explanations ----------------------------------------------------------------------


CARDS = [
    ("Saldo inicial", "tip-opening"),
    ("Entradas do mês", "tip-income"),
    ("Despesas do mês", "tip-expense"),
    ("Saldo final", "tip-closing"),
    ("Taxa de economia", "tip-savings"),
]


def test_every_card_has_an_accessible_explanation_control(logged_client, user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 3))

    content = html(logged_client)

    for label, tip in CARDS:
        assert f'aria-label="Como é calculado: {label}" aria-describedby="{tip}"' in content
        assert f'id="{tip}" role="tooltip"' in content
    assert content.count("data-tip") == 5
    assert "@keydown.escape" in content and "@focus" in content  # keyboard and touch


def test_savings_explanation_shows_the_formula_with_the_months_values(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "6500.00", when=date(2026, 10, 3))
    make_transaction(user, "expense", "5000.00", when=date(2026, 10, 4))

    content = html(logged_client)
    tip = content.split('id="tip-savings"')[1].split("</div>")[0]

    assert "dividido pelas entradas" in tip
    assert "(R$ 6.500,00 − R$ 5.000,00) ÷ R$ 6.500,00 × 100" in tip


def test_closing_explanation_uses_the_opening_and_the_totals(logged_client, user, make_transaction):
    make_transaction(user, "income", "300.00", when=date(2026, 9, 3))
    make_transaction(user, "income", "100.00", when=date(2026, 10, 3))
    make_transaction(user, "expense", "40.00", when=date(2026, 10, 4))

    tip = html(logged_client).split('id="tip-closing"')[1].split("</div>")[0]

    assert "R$ 300,00 + R$ 100,00 − R$ 40,00" in tip


def test_opening_explanation_names_the_day_before_the_month(logged_client, user, make_transaction):
    make_transaction(user, "income", "300.00", when=date(2026, 9, 3))

    tip = html(logged_client).split('id="tip-opening"')[1].split("</div>")[0]

    assert "anterior a 01/10/2026" in tip
    assert "30/09/2026" in tip


def test_change_explanation_shows_the_formula_and_the_base(logged_client, user, make_transaction):
    make_transaction(user, "expense", "100.00", when=date(2026, 9, 3))
    make_transaction(user, "expense", "150.00", when=date(2026, 10, 3))

    tip = html(logged_client).split('id="tip-expense"')[1].split("</div>")[0]

    assert "setembro de 2026" in tip
    assert "(R$ 150,00 − R$ 100,00) ÷ R$ 100,00" in tip


def test_explanation_without_a_base_says_the_card_shows_no_base(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 3))

    tip = html(logged_client).split('id="tip-income"')[1].split("</div>")[0]

    assert "Não houve entradas em setembro de 2026" in tip
    assert 'mostra "sem base"' in tip


# --- categories tab -------------------------------------------------------------------------


def make_seven(user, make_transaction, make_category):
    for index in range(7):
        category = make_category(user, f"Cat {index}", color="blue")
        make_transaction(
            user, "expense", f"{10 * (index + 1)}.00", when=date(2026, 10, 2), category=category
        )


def test_categories_tab_lists_all_of_them_without_other(
    logged_client, user, make_transaction, make_category
):
    make_seven(user, make_transaction, make_category)

    response = page(logged_client, "dashboard_categories")
    content = response.content.decode()

    assert all(f"Cat {i}" in content for i in range(7))
    assert "Outras" not in content
    assert "R$ 280,00" in content.split("data-category-total>")[1].split("</td>")[0]
    assert 'id="chart-categories"' in content
    assert 'id="chart-cashflow"' not in content


def test_overview_donut_groups_the_small_categories(
    logged_client, user, make_transaction, make_category
):
    make_seven(user, make_transaction, make_category)

    content = html(logged_client)

    assert "Outras" in content
    assert "Cat 0" not in content  # grouped away


def test_categories_tab_without_expenses(logged_client, user, make_transaction):
    make_transaction(user, "income", "50.00", when=date(2026, 10, 2))

    content = html(logged_client, "dashboard_categories")

    assert "Nenhum gasto registrado neste mês." in content
    assert 'id="chart-categories"' not in content


# --- flow tab -------------------------------------------------------------------------------


def test_flow_tab_has_the_two_daily_charts_and_the_summary(logged_client, user, make_transaction):
    make_transaction(user, "income", "1000.00", when=date(2026, 9, 3))
    make_transaction(user, "expense", "250.00", when=date(2026, 10, 3))

    response = page(logged_client, "dashboard_flow")
    content = response.content.decode()

    assert 'id="chart-cashflow"' in content and 'id="chart-balance"' in content
    assert 'id="chart-categories"' not in content
    assert "R$ 1.000,00" in content.split("data-flow-summary>")[1].split("</p>")[0]
    assert set(response.context["chart_data"]) == {
        "days",
        "income",
        "expense",
        "balance",
        "weeks",
        "lowest",
    }


def test_flow_tab_shows_the_closing_the_lowest_and_the_balance_from_the_opening(
    logged_client, user, make_transaction
):
    known_october(user, make_transaction)

    content = html(logged_client, "dashboard_flow")
    summary = text_of(content.split("data-flow-summary>")[1].split("</p>")[0])
    lowest = content.split("data-lowest-balance>")[1].split("</p>")[0]
    data = embedded_data(content)

    assert summary == "Saldo inicial R$ 1.250,00 → saldo final R$ 4.425,35 (outubro de 2026)"
    assert lowest == "Menor saldo: − R$ 1.208,15 em 04/10 · termina o mês em R$ 4.425,35"
    assert data["balance"] == KNOWN_BALANCE
    assert data["lowest"] == 3


# --- transactions tab -----------------------------------------------------------------------


def test_transactions_tab_lists_every_transaction_of_the_month_newest_first(
    logged_client, user, make_transaction
):
    for day in range(1, 9):
        make_transaction(
            user, "income", "1.00", when=date(2026, 10, day), description=f"d{day:02d}"
        )
    for day in range(1, 4):
        make_transaction(user, "income", "1.00", when=date(2026, 9, day), description=f"s{day:02d}")

    response = page(logged_client, "dashboard_transactions")
    content = response.content.decode()

    assert [t.description for t in response.context["transactions"]] == [
        f"d{day:02d}" for day in range(8, 0, -1)
    ]
    assert "s01" not in content
    assert "8 lançamentos" in content
    assert f'href="{reverse("transactions:list")}"' in content


def test_transactions_tab_of_an_empty_month(logged_client, user, make_transaction):
    make_transaction(user, "income", "1.00", when=date(2026, 8, 1))

    content = html(logged_client, "dashboard_transactions")

    assert "Nenhum lançamento em outubro de 2026." in content


# --- charts data and scripts ----------------------------------------------------------------


def test_chart_data_is_embedded_as_json_and_escaped(
    logged_client, user, make_transaction, make_category
):
    evil = make_category(user, "</script><b>x", color="blue")
    make_transaction(user, "expense", "10.00", when=date(2026, 10, 3), category=evil)

    content = html(logged_client)

    assert "</script><b>x" not in content
    payload = content.split('id="dashboard-data" type="application/json">')[1].split("</script>")[0]
    data = json.loads(payload)
    assert data["categories"][0]["name"] == "</script><b>x"
    assert data["categories"][0]["amount"] == 10.0
    assert len(data["days"]) == len(data["balance"]) == 31


@pytest.mark.parametrize("route", ["home", "dashboard_flow"])
def test_embedded_chart_values_match_the_month_and_close_with_the_cards(
    logged_client, user, make_transaction, route
):
    known_october(user, make_transaction)

    response = page(logged_client, route)
    data = embedded_data(response.content.decode())
    summary = response.context["summary"]

    assert data["income"] == KNOWN_INCOME
    assert data["expense"] == KNOWN_EXPENSE
    assert data["balance"] == KNOWN_BALANCE
    assert data["weeks"]["labels"][-1] == ["Sem 5", "29–31"]
    assert data["weeks"]["income"] == [5600.0, 0.0, 100.0, 0.0, 0.0]
    assert data["weeks"]["expense"] == [2458.15, 0.0, 0.0, 0.0, 66.5]
    for series in (data["income"], data["weeks"]["income"]):
        assert round(sum(series), 2) == float(summary.income) == 5700.0
    for series in (data["expense"], data["weeks"]["expense"]):
        assert round(sum(series), 2) == float(summary.expense) == 2524.65
    assert data["balance"][-1] == float(summary.closing) == 4425.35


def test_daily_series_follows_the_length_of_the_month(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 2, 3))

    payload = html(logged_client, month="2026-02").split(
        'id="dashboard-data" type="application/json">'
    )[1]

    assert len(json.loads(payload.split("</script>")[0])["days"]) == 28


def test_the_transactions_tab_loads_no_chart_script(logged_client, user, make_transaction):
    make_transaction(user, "income", "1.00", when=date(2026, 10, 3))

    content = html(logged_client, "dashboard_transactions")

    assert "chart.umd.min.js" not in content and "dashboard-data" not in content


def test_page_loads_scripts_locally_only(logged_client, user, make_transaction):
    make_transaction(user, "income", "1.00", when=date(2026, 10, 3))

    content = html(logged_client)

    assert "dist/js/chart.umd.min.js" in content
    assert "js/dashboard-charts.js" in content
    assert "https://" not in "".join(
        line for line in content.splitlines() if "<script" in line and "src=" in line
    )


# --- isolation ------------------------------------------------------------------------------


@pytest.mark.parametrize("route", TAB_ROUTES)
def test_pages_only_show_the_users_own_data(
    logged_client, user, other_user, make_transaction, make_category, route
):
    secret = make_category(other_user, "Segredo da Bia")
    make_transaction(user, "income", "10.00", when=date(2026, 10, 3), description="Meu")
    make_transaction(
        other_user,
        "expense",
        "55.00",
        when=date(2026, 10, 3),
        description="Da Bia",
        category=secret,
    )
    make_transaction(other_user, "income", "900.00", when=date(2026, 9, 3), description="Da Bia 2")

    content = html(logged_client, route)

    assert "Da Bia" not in content and "Segredo da Bia" not in content
    assert "900,00" not in content


@pytest.mark.parametrize("route", ["home", "dashboard_flow"])
def test_embedded_chart_data_only_carries_the_users_own_numbers(
    logged_client, user, other_user, make_transaction, make_category, route
):
    secret = make_category(other_user, "Segredo da Bia")
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2), description="Meu")
    make_transaction(other_user, "income", "700.00", when=date(2026, 9, 2))
    make_transaction(other_user, "expense", "55.00", when=date(2026, 10, 2), category=secret)
    make_transaction(other_user, "expense", "900.00", when=date(2026, 10, 5), category=secret)
    make_transaction(other_user, "income", "300.00", when=date(2026, 10, 9))

    content = html(logged_client, route)
    data = embedded_data(content)
    lowest = content.split("data-lowest-balance>")[1].split("</p>")[0]

    assert data["income"] == [0.0, 10.0] + [0.0] * 29
    assert data["expense"] == [0.0] * 31
    assert data["balance"] == [0.0] + [10.0] * 30
    assert data["weeks"]["income"] == [10.0, 0.0, 0.0, 0.0, 0.0]
    assert data["weeks"]["expense"] == [0.0] * 5
    assert data["lowest"] == 0
    assert lowest == "Menor saldo: R$ 0,00 em 01/10 · termina o mês em R$ 10,00"


# --- month field, "Este mês" and the new-transaction shortcut ------------------------------------


def test_month_field_lists_the_months_from_the_first_transaction_and_only_those(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "10.00", when=date(2026, 7, 2))

    response = page(logged_client, month="2026-08")
    content = response.content.decode()

    assert [value for value, _ in response.context["month_options"]] == [
        "2026-10",
        "2026-09",
        "2026-08",
        "2026-07",
    ]
    for label in ("Outubro de 2026", "Setembro de 2026", "Agosto de 2026", "Julho de 2026"):
        assert f">{label}</option>" in content
    assert 'value="2026-08" selected' in content
    assert "Junho de 2026" not in content


def test_month_field_submits_by_get_to_the_same_tab(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 7, 2))

    content = html(logged_client, "dashboard_flow")

    assert '<form method="get" action=""' in content
    assert 'name="month"' in content


def test_this_month_shortcut_is_a_link_away_and_disabled_on_the_current_month(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "10.00", when=date(2026, 7, 2))

    away = html(logged_client, month="2026-09")
    current = html(logged_client)

    assert f'href="{reverse("home")}?month=2026-10" class' in away
    assert "data-current-month" in away and "data-this-month-off" not in away
    # The slot stays on the current month, disabled like the next arrow, so the layout holds still.
    assert "data-current-month" not in current
    assert 'aria-disabled="true" data-this-month-off>Este mês' in current


@pytest.mark.parametrize("route", TAB_ROUTES)
def test_new_transaction_shortcut_is_on_every_tab(logged_client, user, make_transaction, route):
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2))

    content = html(logged_client, route)

    assert f'href="{reverse("transactions:create")}"' in content
    assert "data-new-transaction" in content


def test_empty_account_has_no_header_shortcut(logged_client):
    assert "data-new-transaction" not in html(logged_client)


def test_month_controls_have_a_touch_area_of_44px(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 7, 2))

    content = html(logged_client, month="2026-09")

    assert content.count("h-11 w-11") >= 2  # both arrows
    assert "h-11 w-full" in content  # the month field


# --- hero block, savings phrase and text summaries ----------------------------------------------


def test_hero_shows_the_closing_balance_status_and_opening_without_any_script(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "1000.00", when=date(2026, 9, 5))
    make_transaction(user, "income", "500.00", when=date(2026, 10, 5))

    content = html(logged_client)
    hero = content.split("data-hero>")[1].split("</section>")[0]

    assert "R$ 1.500,00" in hero.split("data-balance>")[1].split("</p>")[0]
    assert "Você está no verde. Continue assim!" in hero
    assert "Começou o mês com" in hero
    assert "R$ 1.000,00" in hero.split("data-opening>")[1].split("</span>")[0]
    assert "chart-hero" in hero


def test_hero_is_only_on_the_overview(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2))

    for route in ("dashboard_categories", "dashboard_flow", "dashboard_transactions"):
        assert "data-hero" not in html(logged_client, route)


def test_hero_has_a_text_alternative_with_the_lowest_and_the_final_balance(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "100.00", when=date(2026, 9, 1))
    make_transaction(user, "expense", "300.00", when=date(2026, 10, 4))
    make_transaction(user, "income", "1000.00", when=date(2026, 10, 9))

    hero = html(logged_client).split("data-hero>")[1]
    label = hero.split('id="chart-hero"')[1].split(">")[0]

    assert "Menor saldo: − R$ 200,00 em 04/10" in label
    assert "Saldo final: R$ 800,00" in label


def test_negative_closing_in_the_hero_is_red_with_the_warning(
    logged_client, user, make_transaction
):
    make_transaction(user, "expense", "50.00", when=date(2026, 10, 2))

    hero = html(logged_client).split("data-hero>")[1].split("</section>")[0]

    assert "text-error-600" in hero.split("data-balance>")[0].rsplit("<p", 1)[1]
    assert "− R$ 50,00" in hero.split("data-balance>")[1].split("</p>")[0]
    assert "Você está no vermelho, cuidado" in hero


@pytest.mark.parametrize(
    ("income", "expense", "phrase"),
    [
        ("1000.00", "754.00", "Sobrou 24,6% de tudo o que entrou neste mês"),
        ("1000.00", "1100.00", "Gastou 10,0% a mais do que entrou neste mês"),
    ],
)
def test_savings_phrase(logged_client, user, make_transaction, income, expense, phrase):
    make_transaction(user, "income", income, when=date(2026, 10, 2))
    make_transaction(user, "expense", expense, when=date(2026, 10, 3))

    content = html(logged_client)

    assert phrase in content.split("data-savings-phrase>")[1].split("</p>")[0]


def test_savings_phrase_without_income(logged_client, user, make_transaction):
    make_transaction(user, "expense", "10.00", when=date(2026, 10, 3))

    content = html(logged_client)

    assert "Sem entradas neste mês" in content.split("data-savings-phrase>")[1].split("</p>")[0]


def test_overview_has_three_indicators_and_no_opening_or_closing_card(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2))

    cards = html(logged_client).split("data-cards>")[1].split("data-hero")[0]

    for label in ("Entradas do mês", "Despesas do mês", "Taxa de economia"):
        assert label in cards
    assert "Saldo inicial" not in cards and "Saldo final" not in cards
    assert cards.count("data-tip") == 3


def test_largest_expense_sentence(logged_client, user, make_transaction):
    make_transaction(user, "expense", "1500.00", when=date(2026, 10, 2), description="Aluguel")
    make_transaction(user, "expense", "20.00", when=date(2026, 10, 3), description="Café")

    content = html(logged_client)

    assert (
        "Maior despesa: dia 02, R$ 1.500,00 (Aluguel)"
        in content.split("data-largest-expense>")[1].split("</p>")[0]
    )


def test_largest_expense_description_is_escaped(logged_client, user, make_transaction):
    make_transaction(user, "expense", "20.00", when=date(2026, 10, 3), description="<b>x</b>")

    sentence = html(logged_client).split("data-largest-expense>")[1].split("</p>")[0]

    assert "&lt;b&gt;x&lt;/b&gt;" in sentence
    assert "<b>" not in sentence


def test_no_expense_sentence(logged_client, user, make_transaction):
    make_transaction(user, "income", "20.00", when=date(2026, 10, 3))

    sentence = html(logged_client).split("data-largest-expense>")[1].split("</p>")[0]

    assert sentence == "Nenhuma despesa neste mês."


def test_lowest_balance_sentence(logged_client, user, make_transaction):
    make_transaction(user, "income", "1250.00", when=date(2026, 9, 20))
    make_transaction(user, "expense", "1500.00", when=date(2026, 10, 2))
    make_transaction(user, "expense", "745.80", when=date(2026, 10, 3))
    make_transaction(user, "expense", "212.35", when=date(2026, 10, 4))
    make_transaction(user, "income", "5600.00", when=date(2026, 10, 5))

    sentence = html(logged_client).split("data-lowest-balance>")[1].split("</p>")[0]

    assert sentence == "Menor saldo: − R$ 1.208,15 em 04/10 · termina o mês em R$ 4.391,85"


def test_lowest_balance_sentence_of_a_month_without_transactions(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "500.00", when=date(2026, 8, 2))

    sentence = html(logged_client).split("data-lowest-balance>")[1].split("</p>")[0]

    assert sentence == "Sem lançamentos neste mês; o saldo ficou em R$ 500,00."


def test_the_flow_tab_has_the_two_sentences_too(logged_client, user, make_transaction):
    make_transaction(user, "expense", "20.00", when=date(2026, 10, 3))

    content = html(logged_client, "dashboard_flow")

    assert "data-largest-expense" in content and "data-lowest-balance" in content


def test_money_values_use_tabular_numerals(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2))

    content = html(logged_client)

    assert content.split("data-balance>")[0].rsplit("<p", 1)[1].count("tabular-nums") == 1
    assert "tabular-nums" in content.split("data-month-income>")[0].rsplit("<p", 1)[1]


def test_flow_toggle_is_in_the_page_but_hidden_until_the_script_runs(
    logged_client, user, make_transaction
):
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2))

    toggle = html(logged_client).split("data-flow-toggle>")[0].rsplit("<div", 1)[1]

    assert "hidden" in toggle


def test_negative_savings_rate_uses_the_minus_sign(logged_client, user, make_transaction):
    make_transaction(user, "income", "1000.00", when=date(2026, 10, 2))
    make_transaction(user, "expense", "1100.00", when=date(2026, 10, 3))

    value = html(logged_client).split("data-savings-rate>")[1].split("</p>")[0]

    assert value == "− 10,0%"


def test_hero_does_not_clip_the_explanations(logged_client, user, make_transaction):
    """The "i" explanations open inside the hero and overflow it: it must not clip them."""
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2))

    opening_tag = html(logged_client).split("<section")[1].split("data-hero>")[0]

    assert "data-hero" not in opening_tag  # the split landed on the hero's own tag
    assert "overflow-hidden" not in opening_tag
