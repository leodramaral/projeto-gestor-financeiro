from datetime import date
from decimal import Decimal

import pytest
from django.utils import timezone

from transactions.forms import TransactionForm

pytestmark = pytest.mark.django_db


def data(**overrides):
    base = {
        "kind": "expense",
        "amount": "25.90",
        "date": "2026-10-01",
        "description": "Almoço",
    }
    base.update(overrides)
    return base


def test_valid_form():
    form = TransactionForm(data())

    assert form.is_valid(), form.errors
    assert form.cleaned_data["amount"] == Decimal("25.90")
    assert form.cleaned_data["date"] == date(2026, 10, 1)


@pytest.mark.parametrize("amount", ["1234,56", "1234.56", "0,01", "0.01"])
def test_accepts_decimal_comma_and_point(amount):
    assert TransactionForm(data(amount=amount)).is_valid()


def test_comma_is_read_as_decimal_separator():
    form = TransactionForm(data(amount="1234,56"))

    assert form.is_valid()
    assert form.cleaned_data["amount"] == Decimal("1234.56")


@pytest.mark.parametrize(
    ("amount", "expected"),
    [("1.234,56", "1234.56"), ("12.345,67", "12345.67"), ("1.234.567,89", "1234567.89")],
)
def test_thousands_separator_is_read_only_with_a_decimal_comma(amount, expected):
    form = TransactionForm(data(amount=amount))

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
    form = TransactionForm(data(amount=amount))

    assert not form.is_valid()
    assert message in " ".join(form.errors["amount"])


@pytest.mark.parametrize("value", ["2026-02-31", "31/02/2026", "ontem", "2026-13-01", ""])
def test_invalid_date(value):
    form = TransactionForm(data(date=value))

    assert not form.is_valid()
    assert "date" in form.errors


def test_accepts_brazilian_date_format():
    form = TransactionForm(data(date="15/03/2026"))

    assert form.is_valid()
    assert form.cleaned_data["date"] == date(2026, 3, 15)


@pytest.mark.parametrize("kind", ["", "transfer", "INCOME"])
def test_invalid_kind(kind):
    form = TransactionForm(data(kind=kind))

    assert not form.is_valid()
    assert "kind" in form.errors


def test_description_required_and_stripped():
    assert "description" in TransactionForm(data(description="   ")).errors
    assert TransactionForm(data(description="  Café  ")).is_valid()
    form = TransactionForm(data(description="  Café  "))
    form.is_valid()
    assert form.cleaned_data["description"] == "Café"


def test_description_too_long():
    form = TransactionForm(data(description="x" * 201))

    assert "200 caracteres" in " ".join(form.errors["description"])


def test_all_fields_empty_report_each_one():
    form = TransactionForm({})

    assert not form.is_valid()
    assert set(form.errors) == {"kind", "amount", "date", "description"}


def test_new_form_defaults_date_to_today():
    assert TransactionForm().fields["date"].initial == timezone.localdate()


def test_form_never_exposes_the_owner():
    assert "user" not in TransactionForm().fields


def test_amount_input_carries_the_mask():
    attrs = TransactionForm().fields["amount"].widget.attrs

    assert "mask(" in attrs["x-data"]
    assert attrs["x-on:input"] == "$el.value = mask($el.value)"
    assert attrs["inputmode"] == "numeric"


def test_kind_is_a_radio_without_empty_choice_or_preselection():
    kind = TransactionForm().fields["kind"]

    assert [value for value, _ in kind.choices] == ["income", "expense"]
    assert TransactionForm()["kind"].value() is None
