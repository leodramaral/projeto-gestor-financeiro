from datetime import date

import pytest

from transactions.periods import first_transaction_month, resolve_month, shift_month

TODAY = date(2026, 10, 15)


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


def test_no_parameter_means_the_current_month():
    view = resolve_month(None, TODAY)

    assert (view.start, view.end) == (date(2026, 10, 1), date(2026, 10, 31))
    assert view.next is None
    assert view.previous == date(2026, 9, 1)
    assert view.param == "2026-10"


def test_a_valid_past_month_is_used_and_has_a_next_month():
    view = resolve_month("2026-08", TODAY, first_month=date(2026, 1, 1))

    assert (view.start, view.end) == (date(2026, 8, 1), date(2026, 8, 31))
    assert view.previous == date(2026, 7, 1)
    assert view.next == date(2026, 9, 1)
    assert view.has_previous


@pytest.mark.parametrize("raw", ["2026-13", "2026-00", "abc", "", "2026-1", "2026-10-01", "26-10"])
def test_unusable_values_fall_back_to_the_current_month(raw):
    assert resolve_month(raw, TODAY).start == date(2026, 10, 1)


@pytest.mark.parametrize("raw", ["2026-11", "2027-01", "9999-12"])
def test_future_months_fall_back_to_the_current_month(raw):
    assert resolve_month(raw, TODAY).start == date(2026, 10, 1)


@pytest.mark.parametrize(
    ("raw", "today", "last_day"),
    [
        ("2024-02", date(2026, 10, 15), date(2024, 2, 29)),
        ("2025-02", date(2026, 10, 15), date(2025, 2, 28)),
        ("2026-12", date(2026, 12, 31), date(2026, 12, 31)),
        ("2026-01", date(2026, 1, 1), date(2026, 1, 31)),
    ],
)
def test_the_end_of_the_month_is_inclusive_and_calendar_aware(raw, today, last_day):
    assert resolve_month(raw, today).end == last_day


def test_december_links_across_the_year():
    view = resolve_month("2025-12", TODAY)

    assert view.next == date(2026, 1, 1)
    assert resolve_month("2026-01", TODAY).previous == date(2025, 12, 1)


def test_cannot_go_back_past_the_first_transaction_month():
    first = date(2026, 8, 1)

    assert resolve_month("2026-09", TODAY, first).has_previous
    assert not resolve_month("2026-08", TODAY, first).has_previous
    assert not resolve_month("2026-08", TODAY, None).has_previous  # no history: only today


def test_label_is_in_portuguese():
    assert resolve_month("2026-10", TODAY).label == "outubro de 2026"
    assert resolve_month("2026-03", TODAY).label == "março de 2026"


def test_first_transaction_month_ignores_other_users(user, other_user, make_transaction):
    make_transaction(other_user, "income", "1.00", when=date(2020, 1, 20))
    make_transaction(user, "income", "1.00", when=date(2026, 8, 20))
    make_transaction(user, "income", "1.00", when=date(2026, 9, 2))

    assert first_transaction_month(user) == date(2026, 8, 1)


def test_first_transaction_month_without_transactions(user):
    assert first_transaction_month(user) is None


def test_month_before_the_first_transaction_is_raised_to_it():
    first = date(2026, 7, 1)

    view = resolve_month("2026-03", TODAY, first)

    assert view.start == first
    assert not view.has_previous
    assert view.next == date(2026, 8, 1)
