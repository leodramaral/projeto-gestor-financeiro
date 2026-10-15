"""Checks on the model's final text before it reaches the user. Pure, so it needs no client or
database: given the text and the successful spending results of *this* question, it says why the
text must not be shown, or None when it can.

What it proves: a query happened, every amount in reais written with digits is one the query
returned (rounded forms such as "4 mil reais" are refused), and the text is short. What it cannot
prove is that a text without amounts stays on topic, or an amount written out in words.
"""

import re
from decimal import Decimal, InvalidOperation

NO_QUERY = "no_query"
VALUE_MISMATCH = "value_mismatch"
TOO_LONG = "too_long"
MAX_CHARS = 1200

_AMOUNT = r"\d[\d.,]*"
# `R$ 1.234,56`, `R$ -5.000,00`, `R$ **900,00**`, `BRL 5.000,00` and `900 reais`.
_AMOUNTS = re.compile(
    rf"(?:R\$|BRL)\s*[*_~]*\s*-?\s*({_AMOUNT})|({_AMOUNT})\s*reais", re.IGNORECASE
)
# "4 mil reais", "R$ 2 mil", "R$ 1,5 milhão": a rounded amount the tool never returned.
_SCALE = r"(?:mil|milh(?:ão|ões|ao|oes)|k)\b"
_SCALED = re.compile(
    rf"(?:R\$|BRL)\s*[*_~]*\s*-?\s*{_AMOUNT}\s*{_SCALE}|{_AMOUNT}\s*{_SCALE}\s*reais",
    re.IGNORECASE,
)
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


def _without_names(text, results):
    """`text` with every category name removed: a name such as "Mesada R$ 200" is the user's data,
    not an amount the model is claiming."""
    names = {c["name"] for result in results for c in result["categories"] if c["name"]}
    for name in sorted(names, key=len, reverse=True):
        text = text.replace(name, " ")
    return text


def _matches(text, results):
    allowed = _allowed(results)
    text = _without_names(text, results)
    if _SCALED.search(text):
        return False
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
