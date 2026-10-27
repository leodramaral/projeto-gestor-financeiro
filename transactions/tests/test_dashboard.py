from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse

from transactions.dashboard import (
    TOP_CATEGORIES,
    build_dashboard,
    build_summary,
    category_slices,
    chart_data,
    daily_series,
    largest_expense,
    lowest_balance,
    month_transactions,
    opening_balance,
    weekly_series,
)
from transactions.models import Category, current_balance
from transactions.periods import resolve_month

pytestmark = pytest.mark.django_db

TODAY = date(2026, 10, 15)


def dec(value):
    return Decimal(value)


def month_of(raw="2026-10", today=TODAY):
    return resolve_month(raw, today)


# --- balance of the month ---------------------------------------------------------------------


def test_opening_balance_is_everything_before_the_month(user, make_transaction):
    make_transaction(user, "income", "1000.00", when=date(2025, 1, 10))
    make_transaction(user, "expense", "250.00", when=date(2026, 9, 30))
    make_transaction(user, "income", "50.00", when=date(2026, 10, 1))

    summary = build_summary(user, month_of())

    assert summary.opening == dec("750.00")
    assert summary.closing == dec("800.00")


def test_opening_balance_of_a_month_is_the_closing_of_the_previous_one(user, make_transaction):
    make_transaction(user, "income", "500.00", when=date(2026, 8, 3))
    make_transaction(user, "expense", "120.50", when=date(2026, 9, 9))
    make_transaction(user, "income", "70.00", when=date(2026, 10, 9))
    make_transaction(user, "expense", "30.00", when=date(2026, 10, 20))

    closings = {raw: build_summary(user, month_of(raw)).closing for raw in ("2026-09", "2026-10")}
    opening_october = build_summary(user, month_of("2026-10")).opening

    assert opening_october == closings["2026-09"] == dec("379.50")


def test_closing_equals_opening_plus_income_minus_expense(user, make_transaction):
    make_transaction(user, "income", "300.00", when=date(2026, 9, 1))
    make_transaction(user, "income", "100.00", when=date(2026, 10, 1))
    make_transaction(user, "expense", "40.00", when=date(2026, 10, 2))

    summary = build_summary(user, month_of())

    assert summary.closing == summary.opening + summary.income - summary.expense == dec("360.00")


def test_closing_includes_future_dated_transactions_inside_the_month(user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 5))
    make_transaction(user, "expense", "30.00", when=date(2026, 10, 28))  # after "today"

    assert build_summary(user, month_of()).closing == dec("70.00")


def test_closing_ignores_transactions_after_the_month(user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 10, 5))
    make_transaction(user, "income", "999.00", when=date(2026, 11, 2))

    summary = build_summary(user, month_of())

    assert summary.closing == dec("100.00")
    # The list balance counts everything, so the two only agree when nothing is dated later.
    assert current_balance(user) == dec("1099.00")


def test_closing_matches_the_list_balance_when_nothing_is_later(user, make_transaction):
    make_transaction(user, "income", "1234.56", when=date(2025, 3, 1))
    make_transaction(user, "expense", "34.06", when=date(2026, 9, 1))

    assert build_summary(user, month_of()).closing == current_balance(user) == dec("1200.50")


@pytest.mark.parametrize(
    ("kind", "amount", "status"),
    [("expense", "5.00", "negative"), ("income", "5.00", "positive"), (None, None, "zero")],
)
def test_status_follows_the_closing_balance(user, make_transaction, kind, amount, status):
    if kind:
        make_transaction(user, kind, amount, when=date(2026, 10, 2))
    else:
        make_transaction(user, "income", "5.00", when=date(2026, 10, 2))
        make_transaction(user, "expense", "5.00", when=date(2026, 10, 3))

    assert build_summary(user, month_of()).status == status


def test_status_reads_the_closing_of_the_chosen_month(user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 8, 1))
    make_transaction(user, "expense", "150.00", when=date(2026, 9, 1))

    assert build_summary(user, month_of("2026-08")).status == "positive"
    assert build_summary(user, month_of("2026-09")).status == "negative"


# --- month cards ----------------------------------------------------------------------------


def test_month_totals_ignore_other_months(user, make_transaction):
    make_transaction(user, "income", "300.00", when=date(2026, 10, 1))
    make_transaction(user, "expense", "100.00", when=date(2026, 10, 31))
    make_transaction(user, "expense", "999.00", when=date(2026, 9, 30))
    make_transaction(user, "expense", "888.00", when=date(2026, 11, 1))

    summary = build_summary(user, month_of())

    assert summary.income == dec("300.00")
    assert summary.expense == dec("100.00")
    assert summary.savings_rate == dec("66.7")


def test_totals_follow_the_chosen_month(user, make_transaction):
    make_transaction(user, "expense", "70.00", when=date(2026, 8, 31))
    make_transaction(user, "expense", "30.00", when=date(2026, 9, 1))

    assert build_summary(user, month_of("2026-08")).expense == dec("70.00")
    assert build_summary(user, month_of("2026-09")).expense == dec("30.00")


def test_change_against_the_previous_month(user, make_transaction):
    make_transaction(user, "expense", "100.00", when=date(2026, 9, 10))
    make_transaction(user, "expense", "150.00", when=date(2026, 10, 10))
    make_transaction(user, "income", "200.00", when=date(2026, 9, 10))
    make_transaction(user, "income", "100.00", when=date(2026, 10, 10))

    summary = build_summary(user, month_of())

    assert summary.expense_change == 50
    assert summary.income_change == -50
    assert (summary.previous_income, summary.previous_expense) == (dec("200.00"), dec("100.00"))


def test_change_compares_with_the_month_before_the_chosen_one(user, make_transaction):
    make_transaction(user, "expense", "100.00", when=date(2026, 7, 10))
    make_transaction(user, "expense", "120.00", when=date(2026, 8, 10))
    make_transaction(user, "expense", "999.00", when=date(2026, 10, 10))

    assert build_summary(user, month_of("2026-08")).expense_change == 20


def test_change_crosses_the_year_boundary(user, make_transaction):
    make_transaction(user, "expense", "100.00", when=date(2025, 12, 31))
    make_transaction(user, "expense", "200.00", when=date(2026, 1, 1))

    assert build_summary(user, month_of("2026-01", date(2026, 1, 31))).expense_change == 100


def test_no_change_without_a_base(user, make_transaction):
    make_transaction(user, "income", "200.00", when=date(2026, 10, 10))

    summary = build_summary(user, month_of())

    assert summary.income_change is None
    assert summary.expense_change is None


def test_savings_rate_is_unavailable_without_income(user, make_transaction):
    make_transaction(user, "expense", "80.00", when=date(2026, 10, 10))

    assert build_summary(user, month_of()).savings_rate is None


# --- daily series ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "days"), [("2026-02", 28), ("2028-02", 29), ("2026-09", 30), ("2026-10", 31)]
)
def test_series_has_one_point_per_day_of_the_month(user, raw, days):
    month = month_of(raw, date(2030, 1, 1))

    points = daily_series(user, month, Decimal("0"))

    assert len(points) == days
    assert [p.label for p in points][:3] == ["1", "2", "3"]
    assert points[-1].label == str(days)


def test_empty_days_are_zero_and_the_balance_holds(user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 9, 3))
    make_transaction(user, "expense", "30.00", when=date(2026, 9, 5))
    month = month_of("2026-09")

    points = daily_series(user, month, opening_balance(user, month.start))

    assert [p.income for p in points[:5]] == [0, 0, 100, 0, 0]
    assert [p.expense for p in points[:5]] == [0, 0, 0, 0, 30]
    assert [p.balance for p in points[:6]] == [0, 0, 100, 100, 70, 70]
    assert points[-1].balance == 70


def test_series_starts_from_the_opening_balance(user, make_transaction):
    make_transaction(user, "income", "1000.00", when=date(2025, 1, 10))
    make_transaction(user, "expense", "250.00", when=date(2026, 9, 30))
    make_transaction(user, "income", "50.00", when=date(2026, 10, 1))
    month = month_of()

    points = daily_series(user, month, opening_balance(user, month.start))

    assert points[0].balance == dec("800.00")
    assert points[1].balance == dec("800.00")


def test_series_adds_up_to_the_cards(user, make_transaction):
    make_transaction(user, "income", "500.00", when=date(2025, 6, 1))
    make_transaction(user, "income", "70.00", when=date(2026, 10, 9))
    make_transaction(user, "income", "30.00", when=date(2026, 10, 9))
    make_transaction(user, "expense", "120.50", when=date(2026, 10, 9))
    make_transaction(user, "expense", "9.50", when=date(2026, 10, 31))

    dashboard = build_dashboard(user, month_of())

    assert sum(p.income for p in dashboard.days) == dashboard.summary.income == dec("100.00")
    assert sum(p.expense for p in dashboard.days) == dashboard.summary.expense == dec("130.00")
    assert dashboard.days[-1].balance == dashboard.summary.closing == dec("470.00")


def test_future_transaction_inside_the_month_appears_on_its_day(user, make_transaction):
    make_transaction(user, "expense", "42.00", when=date(2026, 10, 28))

    points = daily_series(user, month_of(), Decimal("0"))

    assert points[27].expense == dec("42.00")
    assert points[26].balance == 0
    assert points[27].balance == dec("-42.00")


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

    slices = category_slices(user, month_of())

    assert [(s.name, s.amount, s.percent) for s in slices] == [
        ("Mercado", dec("100.00"), 50),
        ("Pets", dec("100.00"), 50),
    ]
    assert sum(s.amount for s in slices) == build_summary(user, month_of()).expense


def test_slices_follow_the_chosen_month(user, make_transaction, make_category):
    pets = make_category(user, "Pets")
    make_transaction(user, "expense", "70.00", when=date(2026, 9, 6), category=pets)
    make_transaction(user, "expense", "10.00", when=date(2026, 10, 6), category=pets)

    assert category_slices(user, month_of("2026-09"))[0].amount == dec("70.00")
    assert category_slices(user, month_of("2026-10"))[0].amount == dec("10.00")


def test_slice_matches_the_filtered_list(logged_client, user, make_transaction, make_category):
    food = make_category(user, "Mercado")
    make_transaction(user, "expense", "12.34", when=date(2026, 10, 3), category=food)
    make_transaction(user, "expense", "7.66", when=date(2026, 10, 9), category=food)
    make_transaction(user, "expense", "5.00", when=date(2026, 10, 9))

    slices = category_slices(user, month_of())
    listed = logged_client.get(reverse("transactions:list"), {"category": food.pk}).context[
        "transactions"
    ]

    amount = next(s.amount for s in slices if s.name == "Mercado")
    assert amount == sum(t.amount for t in listed) == dec("20.00")


def seven_categories(user, make_transaction, make_category):
    for index in range(7):
        category = make_category(user, f"Cat {index}", color="blue")
        make_transaction(
            user, "expense", f"{10 * (index + 1)}.00", when=date(2026, 10, 2), category=category
        )


def test_overview_groups_past_the_five_largest_into_other(user, make_transaction, make_category):
    seven_categories(user, make_transaction, make_category)

    slices = category_slices(user, month_of(), limit=TOP_CATEGORIES)

    assert [s.name for s in slices] == ["Cat 6", "Cat 5", "Cat 4", "Cat 3", "Cat 2", "Outras"]
    assert slices[-1].amount == dec("30.00")
    assert slices[-1].color == "graphite"


def test_the_full_list_has_every_category_and_no_other(user, make_transaction, make_category):
    seven_categories(user, make_transaction, make_category)

    slices = category_slices(user, month_of())

    assert [s.name for s in slices] == [f"Cat {i}" for i in range(6, -1, -1)]
    assert sum(s.amount for s in slices) == dec("280.00")


def test_exactly_the_limit_does_not_create_other(user, make_transaction, make_category):
    for index in range(TOP_CATEGORIES):
        category = make_category(user, f"Cat {index}")
        make_transaction(user, "expense", "10.00", when=date(2026, 10, 2), category=category)

    names = [s.name for s in category_slices(user, month_of(), limit=TOP_CATEGORIES)]

    assert "Outras" not in names and len(names) == TOP_CATEGORIES


def test_no_slices_without_expenses_in_the_month(user, make_transaction):
    make_transaction(user, "income", "50.00", when=date(2026, 10, 2))
    make_transaction(user, "expense", "20.00", when=date(2026, 9, 2))

    assert category_slices(user, month_of()) == []


def test_slice_with_an_unknown_color_falls_back_to_the_default(
    user, make_transaction, make_category
):
    odd = make_category(user, "Estranha")
    Category.objects.filter(pk=odd.pk).update(color="nao-existe")
    make_transaction(user, "expense", "10.00", when=date(2026, 10, 2), category=odd)

    assert category_slices(user, month_of())[0].color == "graphite"


# --- recent and the month's list ------------------------------------------------------------


def test_recent_are_the_five_newest_of_the_month_in_list_order(user, make_transaction):
    for day in range(1, 8):
        make_transaction(user, "income", "1.00", when=date(2026, 10, day), description=f"d{day}")
    make_transaction(user, "income", "1.00", when=date(2026, 9, 30), description="antes")
    make_transaction(user, "income", "1.00", when=date(2026, 11, 1), description="depois")

    recent = build_dashboard(user, month_of()).recent

    assert [t.description for t in recent] == ["d7", "d6", "d5", "d4", "d3"]


def test_month_transactions_are_all_of_the_month_newest_first(user, make_transaction):
    first = make_transaction(user, "income", "1.00", when=date(2026, 10, 3), description="a")
    second = make_transaction(user, "income", "1.00", when=date(2026, 10, 3), description="b")
    make_transaction(user, "income", "1.00", when=date(2026, 9, 3), description="fora")
    make_transaction(user, "income", "1.00", when=date(2026, 10, 31), description="fim")

    rows = month_transactions(user, month_of())

    assert [t.pk for t in rows] == [rows[0].pk, second.pk, first.pk]
    assert [t.description for t in rows] == ["fim", "b", "a"]


# --- chart data -----------------------------------------------------------------------------


def test_chart_data_has_only_the_requested_parts(user, make_transaction, make_category):
    pets = make_category(user, "Pets", color="amber")
    make_transaction(user, "expense", "10.00", when=date(2026, 10, 2), category=pets)
    dashboard = build_dashboard(user, month_of())

    day_keys = {"days", "income", "expense", "balance", "weeks", "lowest"}
    assert set(chart_data(days=dashboard.days)) == day_keys
    assert set(chart_data(categories=dashboard.categories)) == {"categories"}
    assert set(dashboard.chart_data) == day_keys | {"categories"}
    assert len(dashboard.chart_data["days"]) == len(dashboard.chart_data["balance"]) == 31
    assert dashboard.chart_data["categories"][0]["amount"] == 10.0


# --- isolation ------------------------------------------------------------------------------


def test_nothing_of_another_user_leaks_into_the_numbers(
    user, other_user, make_transaction, make_category
):
    secret = make_category(other_user, "Segredo da Bia")
    make_transaction(user, "income", "10.00", when=date(2026, 10, 2), description="Meu")
    make_transaction(other_user, "income", "700.00", when=date(2026, 9, 2), description="Da Bia")
    make_transaction(other_user, "expense", "55.00", when=date(2026, 10, 2), category=secret)
    make_transaction(other_user, "expense", "900.00", when=date(2026, 10, 5), category=secret)
    make_transaction(other_user, "income", "300.00", when=date(2026, 10, 9), description="Da Bia")

    dashboard = build_dashboard(user, month_of())
    data = dashboard.chart_data

    assert dashboard.summary.opening == 0
    assert dashboard.summary.closing == dec("10.00")
    assert dashboard.summary.income == dec("10.00")
    assert dashboard.summary.expense == 0
    assert dashboard.categories == []
    assert [d.income for d in dashboard.days] == [0, 10] + [0] * 29
    assert [d.expense for d in dashboard.days] == [0] * 31
    assert [d.balance for d in dashboard.days] == [0] + [10] * 30
    assert (dashboard.lowest.day, dashboard.lowest.balance) == (date(2026, 10, 1), 0)
    assert data["income"] == [0.0, 10.0] + [0.0] * 29
    assert data["expense"] == [0.0] * 31
    assert data["balance"] == [0.0] + [10.0] * 30
    assert data["weeks"]["income"] == [10.0, 0.0, 0.0, 0.0, 0.0]
    assert data["weeks"]["expense"] == [0.0] * 5
    assert data["lowest"] == 0
    assert dashboard.largest_expense is None
    assert [t.description for t in dashboard.recent] == ["Meu"]
    assert [t.description for t in month_transactions(user, month_of())] == ["Meu"]


# --- weeks, largest expense and lowest balance ------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "spans"),
    [
        ("2026-02", ["1–7", "8–14", "15–21", "22–28"]),
        ("2028-02", ["1–7", "8–14", "15–21", "22–28", "29"]),
        ("2026-09", ["1–7", "8–14", "15–21", "22–28", "29–30"]),
        ("2026-10", ["1–7", "8–14", "15–21", "22–28", "29–31"]),
    ],
)
def test_weeks_are_blocks_of_seven_days_and_the_last_one_holds_the_rest(user, raw, spans):
    month = month_of(raw, today=date(2030, 1, 1))

    weeks = weekly_series(daily_series(user, month, dec("0")))

    assert [w.span for w in weeks] == spans
    assert [w.label for w in weeks] == [f"Sem {n}" for n in range(1, len(spans) + 1)]


def test_weeks_add_up_to_the_month_totals(user, make_transaction):
    make_transaction(user, "income", "5600.00", when=date(2026, 10, 5))
    make_transaction(user, "expense", "1500.00", when=date(2026, 10, 2))
    make_transaction(user, "expense", "745.80", when=date(2026, 10, 7))
    make_transaction(user, "expense", "86.70", when=date(2026, 10, 8))
    make_transaction(user, "expense", "66.50", when=date(2026, 10, 31))
    month = month_of()
    summary = build_summary(user, month)

    weeks = weekly_series(daily_series(user, month, summary.opening))

    assert [w.expense for w in weeks] == [
        dec("2245.80"),
        dec("86.70"),
        dec("0"),
        dec("0"),
        dec("66.50"),
    ]
    assert sum(w.income for w in weeks) == summary.income
    assert sum(w.expense for w in weeks) == summary.expense


def test_chart_data_carries_the_weeks_and_the_lowest_day(user, make_transaction):
    make_transaction(user, "income", "100.00", when=date(2026, 9, 1))
    make_transaction(user, "expense", "300.00", when=date(2026, 10, 4))
    month = month_of()
    days = daily_series(user, month, build_summary(user, month).opening)

    data = chart_data(days=days)

    assert data["weeks"]["labels"][0] == ["Sem 1", "1–7"]
    assert len(data["weeks"]["income"]) == len(data["weeks"]["expense"]) == 5
    assert data["lowest"] == 3  # the 4th day, where the balance dropped to -200


def test_largest_expense_is_the_biggest_single_expense_of_the_month(user, make_transaction):
    make_transaction(user, "expense", "1500.00", when=date(2026, 10, 2), description="Aluguel")
    make_transaction(user, "expense", "200.00", when=date(2026, 10, 3), description="Mercado")
    make_transaction(user, "income", "9000.00", when=date(2026, 10, 5), description="Salário")
    make_transaction(user, "expense", "9000.00", when=date(2026, 9, 5), description="Antes")

    found = largest_expense(user, month_of())

    assert (found.description, found.amount, found.date) == (
        "Aluguel",
        dec("1500.00"),
        date(2026, 10, 2),
    )


def test_largest_expense_tie_goes_to_the_most_recent(user, make_transaction):
    make_transaction(user, "expense", "50.00", when=date(2026, 10, 2), description="Antiga")
    make_transaction(user, "expense", "50.00", when=date(2026, 10, 9), description="Nova")

    assert largest_expense(user, month_of()).description == "Nova"


def test_no_largest_expense_without_expenses(user, make_transaction):
    make_transaction(user, "income", "50.00", when=date(2026, 10, 2))

    assert largest_expense(user, month_of()) is None


def test_lowest_balance_is_the_lowest_end_of_day_and_its_date(user, make_transaction):
    make_transaction(user, "income", "1250.00", when=date(2026, 9, 20))
    make_transaction(user, "expense", "1500.00", when=date(2026, 10, 2))
    make_transaction(user, "expense", "745.80", when=date(2026, 10, 3))
    make_transaction(user, "expense", "212.35", when=date(2026, 10, 4))
    make_transaction(user, "income", "5600.00", when=date(2026, 10, 5))
    month = month_of()

    lowest = lowest_balance(daily_series(user, month, build_summary(user, month).opening), month)

    assert lowest.balance == dec("-1208.15")
    assert lowest.day == date(2026, 10, 4)


def test_lowest_balance_tie_goes_to_the_earliest_day(user, make_transaction):
    make_transaction(user, "income", "500.00", when=date(2026, 9, 20))
    month = month_of()

    lowest = lowest_balance(daily_series(user, month, build_summary(user, month).opening), month)

    assert lowest.balance == dec("500.00")
    assert lowest.day == date(2026, 10, 1)


def test_lowest_balance_without_transactions_is_the_opening_balance_on_day_one(user):
    month = month_of()

    lowest = lowest_balance(daily_series(user, month, dec("0")), month)

    assert (lowest.day, lowest.balance) == (date(2026, 10, 1), dec("0"))
