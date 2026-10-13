from decimal import Decimal

from django import forms
from django.utils import timezone

from accounts.forms import StyledFormMixin
from transactions.forms import AMOUNT_ERRORS, MIN_AMOUNT, MONEY_MASK_ATTRS, MoneyField

from .models import Goal


class MoneyFieldsMixin:
    """Gives the money inputs the cents mask and the Brazilian format of the transaction form."""

    money_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.money_fields:
            field = self.fields[name]
            field.widget.attrs.update(MONEY_MASK_ATTRS)
            field.localize = True
            custom = getattr(self.Meta, "error_messages", {}).get(name, {})
            field.error_messages.update({k: v for k, v in AMOUNT_ERRORS.items() if k not in custom})


class SavedAmountMixin:
    def clean_saved_amount(self):
        saved = self.cleaned_data["saved_amount"]
        if saved < Decimal("0"):
            raise forms.ValidationError("O valor guardado não pode ser negativo.", code="negative")
        return saved


class GoalForm(MoneyFieldsMixin, SavedAmountMixin, StyledFormMixin, forms.ModelForm):
    money_fields = ("target_amount", "saved_amount")

    class Meta:
        model = Goal
        fields = ("name", "target_amount", "saved_amount", "deadline")
        widgets = {
            "target_amount": forms.TextInput(),
            "saved_amount": forms.TextInput(),
            "deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
        field_classes = {"target_amount": MoneyField, "saved_amount": MoneyField}
        error_messages = {
            "name": {
                "required": "Informe o nome da meta.",
                "max_length": "O nome pode ter no máximo 60 caracteres.",
            },
            "target_amount": {"required": "Informe o valor-alvo."},
            "saved_amount": {"required": "Informe o valor já guardado."},
            "deadline": {"invalid": "Informe uma data válida."},
        }
        help_texts = {
            "saved_amount": "Total que você já separou para esta meta.",
            "deadline": "Opcional.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        deadline = self.fields["deadline"]
        deadline.input_formats = ["%Y-%m-%d", "%d/%m/%Y"]
        # Picked up by static/js/datepicker.js; without JavaScript it stays a plain date input.
        deadline.widget.attrs.update({"data-datepicker": "", "autocomplete": "off"})
        deadline.widget.attrs["class"] += " pr-11"

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_target_amount(self):
        target = self.cleaned_data["target_amount"]
        if target < MIN_AMOUNT:
            raise forms.ValidationError("O valor deve ser maior que zero.", code="min_amount")
        return target

    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]
        # Only a deadline the user typed is checked: an overdue goal can still get progress.
        if deadline and "deadline" in self.changed_data and deadline < timezone.localdate():
            raise forms.ValidationError("O prazo não pode estar no passado.", code="past_deadline")
        return deadline


class GoalProgressForm(MoneyFieldsMixin, SavedAmountMixin, StyledFormMixin, forms.ModelForm):
    money_fields = ("saved_amount",)

    class Meta:
        model = Goal
        fields = ("saved_amount",)
        widgets = {"saved_amount": forms.TextInput()}
        field_classes = {"saved_amount": MoneyField}
        error_messages = {"saved_amount": {"required": "Informe o valor já guardado."}}
        help_texts = {"saved_amount": "Total que você já separou para esta meta."}
