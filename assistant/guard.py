"""Checks on the model's final text before it reaches the user. Pure, so it needs no client or
database: given the text and the successful spending results of *this* question, it says why the
text must not be shown, or None when it can.

What it proves: a query happened, every amount in reais is one the query returned, and the text is
short. What it cannot prove is that a text without amounts stays on topic.
"""

import re
from decimal import Decimal, InvalidOperation

NO_QUERY = "no_query"
VALUE_MISMATCH = "value_mismatch"
TOO_LONG = "too_long"
MAX_CHARS = 1200

_AMOUNT = r"\d[\d.,]*"
_AMOUNTS = re.compile(rf"R\$\s*({_AMOUNT})|({_AMOUNT})\s*reais", re.IGNORECASE)
_THOUSANDS = re.compile(r"\d{1,3}(?:\.\d{3})+")


def _to_decimal(raw):
    """`1.234,56`, `1234,56`, `1234.56` and `1.234` (thousands) as a Decimal."""
    raw = raw.rstrip(".,")
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif _THOUSANDS.fullmatch(raw):
        raw = raw.replace(".", "")
    return Decimal(raw)


def _cited(text):
    return [a or b for a, b in _AMOUNTS.findall(text)]


def _allowed(results):
    values = set()
    for result in results:
        values.add(Decimal(result["total"]))
        values.update(Decimal(c["amount"]) for c in result["categories"])
    return values


def _matches(text, results):
    allowed = _allowed(results)
    try:
        return all(_to_decimal(raw) in allowed for raw in _cited(text))
    except InvalidOperation:
        return False


def check_answer(text, results):
    """The reason `text` must be rejected, or None."""
    if not results:
        return NO_QUERY
    if len(text) > MAX_CHARS:
        return TOO_LONG
    if not _matches(text, results):
        return VALUE_MISMATCH
    return None
