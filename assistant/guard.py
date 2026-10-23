"""Checks on the model's final text before it reaches the user. Pure, so it needs no client or
database: given the text and the facts of the successful queries of *this* question, it says why the
text must not be shown, or None when it can.

What it proves: a query happened, every amount in reais written with digits is one the query
returned or a sum (two or three terms) or difference (two terms) of terms the text itself shows,
every percentage is one the query returned or follows from terms the text shows, and the text is
short. It checks the arithmetic, not the label: "Moradia and Transporte add up to R$ 2.400,00"
passes if some terms that are in the text do add up to it. What it cannot prove is that a text
without amounts stays on topic, or an amount written out in words or as a bare number.
"""

import re
from decimal import Decimal, InvalidOperation
from itertools import combinations, permutations

NO_QUERY = "no_query"
VALUE_MISMATCH = "value_mismatch"
TOO_LONG = "too_long"
MAX_CHARS = 1200
# A sum has at most this many terms: more would match almost anything once there are many terms.
MAX_SUM_TERMS = 3
# A percentage that is the ratio of two amounts may be this far from the exact one, in points.
RATIO_TOLERANCE = Decimal(1)

_AMOUNT = r"\d[\d.,]*"
# `R$ 1.234,56`, `R$ -5.000,00`, `R$ **900,00**`, `BRL 5.000,00` and `900 reais`.
_AMOUNTS = re.compile(
    rf"(?:R\$|BRL)\s*[*_~]*\s*-?\s*({_AMOUNT})|({_AMOUNT})\s*reais", re.IGNORECASE
)
# "4 mil reais", "R$ 2 mil", "R$ 1,5 milhão": a rounded amount the tool never returned.
_SCALE = r"(?:mil|milh(?:ão|ões|ao|oes)|k)\b"
_SCALED_AMOUNT = r"\d(?:[\d.,]*\d)?"  # no trailing "." or ",": "R$ 1.200,00. Mil desculpas" is fine
_SCALED = re.compile(
    rf"(?:R\$|BRL)\s*[*_~]*\s*-?\s*{_SCALED_AMOUNT}\s*{_SCALE}"
    rf"|{_SCALED_AMOUNT}\s*{_SCALE}\s*reais",
    re.IGNORECASE,
)
_PERCENTS = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")
_THOUSANDS = re.compile(r"\d{1,3}(?:\.\d{3})+")
_TOTAL_WORD = "total"


def _to_decimal(raw):
    """`1.234,56`, `1234,56`, `1234.56` and `1.234` (thousands) as a Decimal."""
    raw = raw.rstrip(".,")
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif _THOUSANDS.fullmatch(raw):
        raw = raw.replace(".", "")
    return Decimal(raw)


def _cited_amounts(text):
    return [_to_decimal(a or b) for a, b in _AMOUNTS.findall(text)]


def _cited_percents(text):
    return [Decimal(raw.replace(",", ".")) for raw in _PERCENTS.findall(text)]


def _without_names(text, facts):
    """`text` with every name from the user's data removed: a name such as "Mesada R$ 200" is the
    user's data, not an amount the model is claiming."""
    names = {name for fact in facts for name in fact.names}
    for name in sorted(names, key=len, reverse=True):
        text = text.replace(name, " ")
    return text


def _has_word(text, label):
    """Whether `label` is in `text` as a whole word: "Ar" is not in "para"."""
    return re.search(rf"(?<!\w){re.escape(label.lower())}(?!\w)", text) is not None


def _in_view(term, text, cited):
    """Whether the text itself shows `term`: it writes its value, or the name it goes by."""
    if term.value in cited:
        return True
    if term.label is None:
        return _TOTAL_WORD in text
    return bool(term.label) and _has_word(text, term.label)


def _derived_amount(value, terms):
    """`value` is a sum of two or three of the `terms` (values) or the difference of two."""
    for size in range(2, MAX_SUM_TERMS + 1):
        if any(sum(group) == value for group in combinations(terms, size)):
            return True
    return any(a - b == value for a, b in permutations(terms, 2))


def _amount_ok(value, facts, shown):
    base = {term.value for fact in facts for term in fact.amounts}
    return value in base or _derived_amount(value, shown)


def _derived_percent(value, percents, amounts):
    """`value` is a sum of percentages (to within the rounding of the terms and of the sum itself:
    half a point for each) or the ratio of two amounts (to within `RATIO_TOLERANCE`)."""
    for size in range(2, MAX_SUM_TERMS + 1):
        slack = (size + 1) // 2
        if any(abs(sum(group) - value) <= slack for group in combinations(percents, size)):
            return True
    return any(
        b and abs(value - 100 * a / b) <= RATIO_TOLERANCE for a, b in permutations(amounts, 2)
    )


def _percent_ok(value, facts, shown_percents, shown_amounts):
    base = {term.value for fact in facts for term in fact.percents}
    return value in base or _derived_percent(value, shown_percents, shown_amounts)


def _matches(text, facts):
    stripped = _without_names(text, facts)
    if _SCALED.search(stripped):
        return False
    try:
        amounts, percents = _cited_amounts(stripped), _cited_percents(stripped)
    except InvalidOperation:
        return False
    lowered = text.lower()
    # Every term of every query: a term is shown to the reader when the text writes it or names it.
    shown_amounts = [
        term.value for fact in facts for term in fact.amounts if _in_view(term, lowered, amounts)
    ]
    shown_percents = [
        term.value for fact in facts for term in fact.percents if _in_view(term, lowered, percents)
    ]
    return all(_amount_ok(value, facts, shown_amounts) for value in amounts) and all(
        _percent_ok(value, facts, shown_percents, shown_amounts) for value in percents
    )


def check_answer(text, facts):
    """The reason `text` must be rejected, or None. `facts` are the `Facts` of this question's
    queries that worked."""
    if not facts:
        return NO_QUERY
    if len(text) > MAX_CHARS:
        return TOO_LONG
    if not _matches(text, facts):
        return VALUE_MISMATCH
    return None
