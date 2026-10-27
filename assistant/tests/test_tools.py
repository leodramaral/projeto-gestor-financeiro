import json
from datetime import date

import pytest
from django.utils import timezone

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


def test_the_current_month_given_explicitly_is_accepted(user, category, make_expense):
    today = timezone.localdate()
    make_expense(user, category("Lazer"), "42.00", today)

    outcome = spending(user, json.dumps({"month": today.strftime("%Y-%m")}))

    assert outcome.data["month"] == today.strftime("%Y-%m")
    assert outcome.data["total"] == "42.00"
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

    assert outcome.data is None
    assert "error" in json.loads(outcome.content)


def test_a_month_before_the_floor_is_an_error_and_no_query(user, django_assert_num_queries):
    with django_assert_num_queries(0):
        outcome = spending(user, json.dumps({"month": "0001-01"}))

    assert outcome.data is None
    assert "January 2000" in json.loads(outcome.content)["error"]


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
    assert "future" in json.loads(outcome.content)["error"]


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
    assert "user_id" in json.loads(outcome.content)["error"]


def test_an_unknown_tool_is_an_error_and_no_query(user, django_assert_num_queries):
    with django_assert_num_queries(0):
        outcome = run_tool(user, "get_balance", "{}")

    assert outcome.data is None and outcome.decline is None
    assert "Unknown tool" in json.loads(outcome.content)["error"]


@pytest.mark.parametrize("arguments", ["not json", "[]", "3", '"x"'])
def test_arguments_must_be_a_json_object(user, arguments):
    outcome = spending(user, arguments)

    assert outcome.data is None
    assert "error" in json.loads(outcome.content)


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
