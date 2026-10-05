import re
from decimal import Decimal

from django import forms
from django.utils import timezone

from accounts.forms import StyledFormMixin

from .models import Transaction

MIN_AMOUNT = Decimal("0.01")

# Thousands separators are only read together with a decimal comma ("1.234,56"): without it,
# "1.500" or "0.001" are ambiguous and stay decimals (and are rejected by the two-places rule).
GROUPED_AMOUNT = re.compile(r"[1-9]\d{0,2}(\.\d{3})+,\d+")

# Cents-style mask: only digits count, and the field shows them as 1.234,56 (no JS: plain text).
MONEY_MASK_ATTRS = {
    "inputmode": "numeric",
    "placeholder": "0,00",
    "autocomplete": "off",
    "x-data": (
        "{ mask(v) { const d = v.replace(/\\D/g, '').slice(0, 14);"
        " return d ? (Number(d) / 100).toLocaleString('pt-BR',"
        " { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : ''; } }"
    ),
    "x-init": "$el.value = $el.value && mask($el.value)",
    "x-on:input": "$el.value = mask($el.value)",
}

AMOUNT_ERRORS = {
    "required": "Informe o valor.",
    "invalid": "Informe um valor numérico válido, como 1234,56.",
    "max_digits": "O valor é grande demais.",
    "max_whole_digits": "O valor é grande demais.",
    "max_decimal_places": "O valor deve ter no máximo duas casas decimais.",
}


class MoneyField(forms.DecimalField):
    """Decimal field that also reads the Brazilian thousands format ("1.234,56")."""

    def to_python(self, value):
        if isinstance(value, str):
            value = value.strip()
            if GROUPED_AMOUNT.fullmatch(value):
                value = value.replace(".", "")
        return super().to_python(value)


class TransactionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ("kind", "amount", "date", "description")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "amount": forms.TextInput(),
            "kind": forms.RadioSelect(),
        }
        field_classes = {"amount": MoneyField}
        error_messages = {
            "kind": {
                "required": "Escolha o tipo do lançamento.",
                "invalid_choice": "Escolha entrada ou despesa.",
            },
            "date": {
                "required": "Informe a data.",
                "invalid": "Informe uma data válida.",
            },
            "description": {
                "required": "Informe a descrição.",
                "max_length": "A descrição pode ter no máximo 200 caracteres.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kind = self.fields["kind"]
        kind.choices = Transaction.Kind.choices
        # Radios become buttons (hidden input + styled label), so they do not take the input style.
        kind.widget.attrs["class"] = "peer sr-only"
        amount = self.fields["amount"]
        amount.widget.attrs.update(MONEY_MASK_ATTRS)
        amount.localize = True
        amount.error_messages.update(AMOUNT_ERRORS)
        self.fields["date"].input_formats = ["%Y-%m-%d", "%d/%m/%Y"]
        if not self.instance.pk:
            self.fields["date"].initial = timezone.localdate()

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount < MIN_AMOUNT:
            raise forms.ValidationError("O valor deve ser maior que zero.", code="min_amount")
        return amount

    def clean_description(self):
        return self.cleaned_data["description"].strip()
