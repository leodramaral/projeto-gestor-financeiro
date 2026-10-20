import json
from datetime import date
from decimal import Decimal

import pytest
from django.utils import timezone

from assistant.facts import Facts, Term
from assistant.tools import (
    DECLINE,
    MAX_CATEGORIES,
    OFF_TOPIC,
    SMALLTALK,
    SPENDING,
    TOOLS,
    run_tool,
)
from transactions.models import Category


def spending(user, arguments="{}"):
    return run_tool(user, SPENDING, arguments)


def amounts(outcome):
    return {c["name"]: c["amount"] for c in outcome.data["categories"]}


def error(outcome):
    return json.loads(outcome.content)["error"]


def current_month():
    return timezone.localdate().strftime("%Y-%m")


@pytest.fixture
def august(user, category, make_expense):
    make_expense(user, category("Alimentação"), "300.00", date(2026, 8, 3))
    make_expense(user, category("Alimentação"), "100.50", date(2026, 8, 20))
    make_expense(user, category("Transporte"), "99.50", date(2026, 8, 7))
    return user


def test_the_two_tools_are_offered_with_closed_schemas():
    names = [t["function"]["name"] for t in TOOLS]

    assert names == [SPENDING, DECLINE]
    assert all(t["function"]["parameters"]["additionalProperties"] is False for t in TOOLS)


def test_spending_of_a_given_month(august):
    outcome = spending(august, '{"month": "2026-08"}')

    assert outcome.data["month"] == "2026-08"
    assert outcome.data["total"] == "500.00"
    assert amounts(outcome) == {"Alimentação": "400.50", "Transporte": "99.50"}
    assert [c["percent"] for c in outcome.data["categories"]] == [80, 20]
    assert json.loads(outcome.content) == outcome.data
    assert outcome.decline is None


def test_the_month_can_come_as_a_dict(august):
    assert spending(august, {"month": "2026-08"}).data["total"] == "500.00"


def test_without_a_month_it_is_the_current_one(user, category, make_expense):
    today = timezone.localdate()
    make_expense(user, category("Lazer"), "42.00", today)

    outcome = spending(user, "{}")

    assert outcome.data["month"] == today.strftime("%Y-%m")
    assert amounts(outcome) == {"Lazer": "42.00"}


def test_a_null_month_is_the_current_one(user):
    assert spending(user, '{"month": null}').data["month"] == timezone.localdate().strftime("%Y-%m")


def test_a_month_without_expenses_is_empty(user, august):
    outcome = spending(august, '{"month": "2026-07"}')

    assert outcome.data["total"] == "0.00"
    assert outcome.data["categories"] == []


def test_incomes_do_not_count(august, make_income):
    make_income(august, "5000.00", date(2026, 8, 5))

    assert spending(august, '{"month": "2026-08"}').data["total"] == "500.00"


@pytest.mark.parametrize(
    "month", ["2026-13", "2026-00", "agosto", "2026-8", "", 202608, ["2026-08"]]
)
def test_a_bad_month_is_an_error_and_no_query(user, month, django_assert_num_queries):
    with django_assert_num_queries(0):
        outcome = spending(user, json.dumps({"month": month}))

    assert outcome.data is None and outcome.facts is None
    assert "error" in json.loads(outcome.content)
    assert not outcome.period  # the model can still fix it


@pytest.mark.parametrize("month", ["agosto", "2026-8", "", 202608, ["2026-08"]])
def test_a_badly_formatted_month_says_the_format_with_an_example(user, month):
    message = error(spending(user, json.dumps({"month": month})))

    assert "YYYY-MM" in message and "2026-08" in message


@pytest.mark.parametrize("month", ["2026-13", "2026-00"])
def test_a_month_that_does_not_exist_says_which_numbers_are_valid(user, month):
    message = error(spending(user, json.dumps({"month": month})))

    assert "does not exist" in message and "01 to 12" in message and "2026-08" in message


def test_a_month_before_the_floor_is_an_error_and_no_query(user, django_assert_num_queries):
    with django_assert_num_queries(0):
        outcome = spending(user, json.dumps({"month": "0001-01"}))

    assert outcome.data is None
    assert outcome.period
    message = error(outcome)
    assert "January 2000" in message
    assert f"2000-01 to {current_month()}" in message


def test_the_floor_month_is_accepted(user):
    assert spending(user, '{"month": "2000-01"}').data["total"] == "0.00"


def test_a_month_before_2025_is_accepted(user):
    assert spending(user, '{"month": "2024-12"}').data["total"] == "0.00"


def test_a_future_month_is_an_error_and_no_query(user, django_assert_num_queries):
    nxt = timezone.localdate().replace(day=1)
    nxt = date(nxt.year + nxt.month // 12, nxt.month % 12 + 1, 1)

    with django_assert_num_queries(0):
        outcome = spending(user, json.dumps({"month": nxt.strftime("%Y-%m")}))

    assert outcome.data is None
    assert outcome.period
    message = error(outcome)
    assert "future" in message
    assert f"latest month available is {current_month()}" in message


def test_more_categories_than_the_limit_are_grouped(user, make_category, make_expense):
    for index in range(MAX_CATEGORIES + 3):
        category = make_category(user, name=f"Cat {index:02d}")
        make_expense(user, category, f"{100 - index}.00", date(2026, 8, 1))

    outcome = spending(user, '{"month": "2026-08"}')
    names = [c["name"] for c in outcome.data["categories"]]

    assert len(names) == MAX_CATEGORIES + 1
    assert names[-1] == "Outras"
    assert sum(float(c["amount"]) for c in outcome.data["categories"]) == float(
        outcome.data["total"]
    )


def test_another_users_spending_never_appears(user, other_user, category, make_expense):
    make_expense(user, category("Transporte"), "10.00", date(2026, 8, 1))
    secret = Category.objects.create(user=other_user, name="Segredo do outro")
    make_expense(other_user, secret, "777.00", date(2026, 8, 1))
    make_expense(other_user, category("Transporte"), "555.00", date(2026, 8, 2))

    outcome = spending(user, '{"month": "2026-08"}')

    assert outcome.data["total"] == "10.00"
    assert "Segredo" not in outcome.content
    assert "777" not in outcome.content and "555" not in outcome.content


def test_a_forged_user_argument_is_refused(user, other_user, django_assert_num_queries):
    with django_assert_num_queries(0):
        outcome = spending(user, json.dumps({"user_id": other_user.pk}))

    assert outcome.data is None
    message = error(outcome)
    assert "user_id" in message
    assert "accepts only: month" in message


def test_an_unknown_tool_is_an_error_and_no_query(user, django_assert_num_queries):
    with django_assert_num_queries(0):
        outcome = run_tool(user, "get_balance", "{}")

    assert outcome.data is None and outcome.decline is None
    message = error(outcome)
    assert "Unknown tool: get_balance" in message
    assert f"Available tools: {SPENDING}, {DECLINE}" in message


@pytest.mark.parametrize("arguments", ["not json", "[]", "3", '"x"'])
def test_arguments_must_be_a_json_object(user, arguments):
    outcome = spending(user, arguments)

    assert outcome.data is None
    assert '{"month": "2026-08"}' in error(outcome)  # the example of what to send


def test_the_decline_tool_shows_its_own_example_of_arguments(user):
    outcome = run_tool(user, DECLINE, "not json")

    assert '{"kind": "off_topic"}' in error(outcome)


@pytest.mark.parametrize(
    ("arguments", "kind"),
    [
        ('{"kind": "off_topic"}', OFF_TOPIC),
        ('{"kind": "smalltalk"}', SMALLTALK),
        ("{}", OFF_TOPIC),
        ('{"kind": "outra coisa"}', OFF_TOPIC),
        ('{"kind": ["x"]}', OFF_TOPIC),
    ],
)
def test_decline_kinds(user, arguments, kind, django_assert_num_queries):
    with django_assert_num_queries(0):
        outcome = run_tool(user, DECLINE, arguments)

    assert outcome.decline == kind
    assert outcome.data is None


def test_decline_refuses_extra_arguments(user):
    outcome = run_tool(user, DECLINE, '{"kind": "off_topic", "user_id": 1}')

    assert outcome.decline is None
    assert "user_id" in json.loads(outcome.content)["error"]


def test_the_facts_are_the_total_and_each_category(august):
    facts = spending(august, '{"month": "2026-08"}').facts

    assert facts == Facts(
        amounts=(
            Term(None, Decimal("500.00")),
            Term("Alimentação", Decimal("400.50")),
            Term("Transporte", Decimal("99.50")),
        ),
        percents=(Term("Alimentação", Decimal(80)), Term("Transporte", Decimal(20))),
        names=frozenset({"Alimentação", "Transporte"}),
    )


def test_a_month_without_expenses_has_only_the_total_as_a_fact(user):
    facts = spending(user, '{"month": "2026-08"}').facts

    assert facts == Facts(amounts=(Term(None, Decimal("0.00")),))


def test_the_grouped_slice_is_a_fact_too(user, make_category, make_expense):
    for index in range(MAX_CATEGORIES + 2):
        make_expense(user, make_category(user, name=f"C{index:02d}"), "10.00", date(2026, 8, 3))

    facts = spending(user, '{"month": "2026-08"}').facts

    assert [term.label for term in facts.amounts][-1] == "Outras"
    assert len(facts.amounts) == MAX_CATEGORIES + 2  # the total, 20 categories and "Outras"
    assert Term("Outras", Decimal("20.00")) in facts.amounts


def test_an_error_and_a_refusal_have_no_facts(user):
    assert spending(user, '{"month": "agosto"}').facts is None
    assert run_tool(user, DECLINE, '{"kind": "off_topic"}').facts is None
