import json
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
    assert "outubro de 2026" in response.content.decode()


def test_selector_links_carry_the_neighbour_months(logged_client, user, make_transaction):
    make_transaction(user, "income", "10.00", when=date(2026, 6, 2))

    content = html(logged_client, month="2026-08")

    assert f'href="{reverse("home")}?month=2026-07"' in content
    assert f'href="{reverse("home")}?month=2026-09"' in content
    assert "agosto de 2026" in content


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


@pytest.mark.parametrize("raw", ["2026-13", "abc", "", "2027-01", "2026-11", "2026-10-05"])
def test_invalid_or_future_month_falls_back_to_the_current_one(
    logged_client, user, make_transaction, raw
):
    make_transaction(user, "income", "10.00", when=date(2026, 8, 2))

    response = page(logged_client, month=raw)

    assert response.status_code == 200
    assert response.context["month"].param == "2026-10"


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
    assert "text-error-500" in content.split("data-balance>")[0].rsplit("<p", 1)[1]
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
    assert set(response.context["chart_data"]) == {"days", "income", "expense", "balance"}


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
