from datetime import date
from decimal import Decimal

import pytest
from django.utils import timezone

from transactions.forms import TransactionForm
from transactions.models import Category

pytestmark = pytest.mark.django_db


def make_form(data=None, *, user=None):
    """The form for a user; `None` sees only the default categories."""
    return TransactionForm(data, user=user)


def data(**overrides):
    base = {
        "kind": "expense",
        "category": Category.other().pk,
        "amount": "25.90",
        "date": "2026-10-01",
        "description": "Almoço",
    }
    base.update(overrides)
    return base


def test_valid_form():
    form = make_form(data())

    assert form.is_valid(), form.errors
    assert form.cleaned_data["amount"] == Decimal("25.90")
    assert form.cleaned_data["date"] == date(2026, 10, 1)


@pytest.mark.parametrize("amount", ["1234,56", "1234.56", "0,01", "0.01"])
def test_accepts_decimal_comma_and_point(amount):
    assert make_form(data(amount=amount)).is_valid()


def test_comma_is_read_as_decimal_separator():
    form = make_form(data(amount="1234,56"))

    assert form.is_valid()
    assert form.cleaned_data["amount"] == Decimal("1234.56")


@pytest.mark.parametrize(
    ("amount", "expected"),
    [("1.234,56", "1234.56"), ("12.345,67", "12345.67"), ("1.234.567,89", "1234567.89")],
)
def test_thousands_separator_is_read_only_with_a_decimal_comma(amount, expected):
    form = make_form(data(amount=amount))

    assert form.is_valid(), form.errors
    assert form.cleaned_data["amount"] == Decimal(expected)


@pytest.mark.parametrize(
    ("amount", "message"),
    [
        ("0", "maior que zero"),
        ("0,00", "maior que zero"),
        ("-5", "maior que zero"),
        ("0,001", "duas casas decimais"),
        ("10,999", "duas casas decimais"),
        ("abc", "valor numérico válido"),
        ("NaN", "valor numérico válido"),
        ("Infinity", "valor numérico válido"),
        ("1.500", "duas casas decimais"),
        ("0.001", "duas casas decimais"),
        ("1.2.3,00", "valor numérico válido"),
        ("01.234,56", "valor numérico válido"),
        ("1.23,45", "valor numérico válido"),
        ("", "Informe o valor"),
        ("99999999999999", "grande demais"),
    ],
)
def test_invalid_amount(amount, message):
    form = make_form(data(amount=amount))

    assert not form.is_valid()
    assert message in " ".join(form.errors["amount"])


@pytest.mark.parametrize("value", ["2026-02-31", "31/02/2026", "ontem", "2026-13-01", ""])
def test_invalid_date(value):
    form = make_form(data(date=value))

    assert not form.is_valid()
    assert "date" in form.errors


def test_accepts_brazilian_date_format():
    form = make_form(data(date="15/03/2026"))

    assert form.is_valid()
    assert form.cleaned_data["date"] == date(2026, 3, 15)


@pytest.mark.parametrize("kind", ["", "transfer", "INCOME"])
def test_invalid_kind(kind):
    form = make_form(data(kind=kind))

    assert not form.is_valid()
    assert "kind" in form.errors


def test_description_required_and_stripped():
    assert "description" in make_form(data(description="   ")).errors
    assert make_form(data(description="  Café  ")).is_valid()
    form = make_form(data(description="  Café  "))
    form.is_valid()
    assert form.cleaned_data["description"] == "Café"


def test_description_too_long():
    form = make_form(data(description="x" * 201))

    assert "200 caracteres" in " ".join(form.errors["description"])


def test_all_fields_empty_report_each_one():
    form = make_form({})

    assert not form.is_valid()
    assert set(form.errors) == {"kind", "amount", "date", "description"}


def test_new_form_defaults_date_to_today():
    assert make_form().fields["date"].initial == timezone.localdate()


def test_form_never_exposes_the_owner():
    assert "user" not in make_form().fields


def test_amount_input_carries_the_mask():
    attrs = make_form().fields["amount"].widget.attrs

    assert "mask(" in attrs["x-data"]
    assert attrs["x-on:input"] == "$el.value = mask($el.value)"
    assert attrs["inputmode"] == "numeric"


def test_kind_is_a_radio_without_empty_choice_or_preselection():
    kind = make_form().fields["kind"]

    assert [value for value, _ in kind.choices] == ["income", "expense"]
    assert make_form()["kind"].value() is None


def test_expense_needs_a_category():
    form = make_form(data(category=""))

    assert not form.is_valid()
    assert "Escolha a categoria da despesa." in form.errors["category"]


def test_expense_with_a_default_or_own_category_is_valid(user, make_category):
    pets = make_category(user, "Pets")

    assert make_form(data(category=pets.pk), user=user).is_valid()
    assert make_form(data(category=Category.other().pk), user=user).is_valid()


def test_income_ignores_the_category_and_saves_without_it():
    form = make_form(data(kind="income", category=Category.other().pk))

    assert form.is_valid(), form.errors
    assert form.cleaned_data["category"] is None


def test_income_does_not_need_a_category():
    assert make_form(data(kind="income", category="")).is_valid()


def test_category_of_another_user_is_refused(user, other_user, make_category):
    theirs = make_category(other_user, "Hobby")

    form = make_form(data(category=theirs.pk), user=user)

    assert not form.is_valid()
    assert "Escolha uma categoria da lista." in form.errors["category"]


@pytest.mark.parametrize("value", ["999999", "abc"])
def test_unknown_category_is_refused(value):
    form = make_form(data(category=value))

    assert not form.is_valid()
    assert "Escolha uma categoria da lista." in form.errors["category"]


def test_category_choices_are_the_defaults_plus_own(user, other_user, make_category):
    make_category(user, "Pets")
    make_category(other_user, "Hobby")

    names = [c.name for c in make_form(user=user).fields["category"].queryset]

    assert "Pets" in names and "Hobby" not in names and "Alimentação" in names
