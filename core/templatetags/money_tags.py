from decimal import Decimal

from django import template
from django.template.defaultfilters import floatformat

register = template.Library()


@register.filter
def brl(value):
    """`R$ 1.234,56`, with a minus sign and a space before the `R$` when negative."""
    amount = Decimal(value)
    sign = "− " if amount < 0 else ""
    return f"{sign}R$ {floatformat(abs(amount), '2g')}"
