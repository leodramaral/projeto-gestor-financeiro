from datetime import timedelta
from decimal import Decimal

import pytest

from goals.forms import GoalForm, GoalProgressForm


def data(**overrides):
    payload = {"name": "Reserva", "target_amount": "500,00", "saved_amount": "0,00", "deadline": ""}
    payload.update(overrides)
    return payload


@pytest.mark.parametrize("target", ["", "0", "0,00", "-5", "abc", "10,123"])
def test_invalid_target_is_rejected(db, target):
    form = GoalForm(data(target_amount=target))
    assert not form.is_valid()
    assert "target_amount" in form.errors


def test_target_error_messages_are_in_portuguese(db):
    assert GoalForm(data(target_amount="0,00")).errors["target_amount"] == [
        "O valor deve ser maior que zero."
    ]
    assert GoalForm(data(target_amount="")).errors["target_amount"] == ["Informe o valor-alvo."]


def test_brazilian_thousands_format_is_read(db):
    form = GoalForm(data(target_amount="1.234,56"))
    assert form.is_valid(), form.errors
    assert form.cleaned_data["target_amount"] == Decimal("1234.56")


@pytest.mark.parametrize("name", ["", "   ", "x" * 61])
def test_invalid_name_is_rejected(db, name):
    form = GoalForm(data(name=name))
    assert not form.is_valid()
    assert "name" in form.errors


def test_name_is_stripped(db):
    form = GoalForm(data(name="  Viagem  "))
    assert form.is_valid(), form.errors
    assert form.cleaned_data["name"] == "Viagem"


def test_deadline_in_the_past_is_rejected(db, today):
    form = GoalForm(data(deadline=(today - timedelta(days=1)).isoformat()))
    assert form.errors["deadline"] == ["O prazo não pode estar no passado."]


def test_deadline_today_future_and_empty_are_accepted(db, today):
    for value in (today, today + timedelta(days=10), ""):
        form = GoalForm(data(deadline=str(value)))
        assert form.is_valid(), form.errors


def test_invalid_deadline_text_is_rejected(db):
    assert GoalForm(data(deadline="amanhã")).errors["deadline"] == ["Informe uma data válida."]


def test_overdue_goal_keeps_its_deadline_when_untouched(make_goal, user, today):
    overdue = today - timedelta(days=10)
    goal = make_goal(user, deadline=overdue)
    form = GoalForm(data(deadline=overdue.isoformat(), saved_amount="100,00"), instance=goal)
    assert form.is_valid(), form.errors


def test_changing_the_deadline_to_the_past_is_rejected(make_goal, user, today):
    goal = make_goal(user, deadline=today + timedelta(days=10))
    form = GoalForm(data(deadline=(today - timedelta(days=2)).isoformat()), instance=goal)
    assert "deadline" in form.errors


def test_saved_amount_can_exceed_the_target(db):
    form = GoalForm(data(saved_amount="800,00"))
    assert form.is_valid(), form.errors


def test_negative_saved_amount_is_rejected(db):
    form = GoalForm(data(saved_amount="-1"))
    assert form.errors["saved_amount"] == ["O valor guardado não pode ser negativo."]


def test_empty_saved_amount_is_rejected(db):
    assert GoalForm(data(saved_amount="")).errors["saved_amount"] == [
        "Informe o valor já guardado."
    ]


def test_progress_form_only_has_the_saved_amount(make_goal, user):
    goal = make_goal(user)
    form = GoalProgressForm({"saved_amount": "200,00"}, instance=goal)
    assert list(form.fields) == ["saved_amount"]
    assert form.is_valid(), form.errors
    assert form.save().saved_amount == Decimal("200.00")


def test_progress_form_rejects_negative(make_goal, user):
    form = GoalProgressForm({"saved_amount": "-3"}, instance=make_goal(user))
    assert "saved_amount" in form.errors
