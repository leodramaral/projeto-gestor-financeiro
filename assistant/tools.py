"""What the model may do: two tools, both read-only.

`get_spending_by_category` reads the signed-in user's expenses; `decline_out_of_scope` only
records that the question is not about that. The user always comes from the caller (the request),
never from the arguments the model produces.
"""

import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.utils import timezone

from transactions.dashboard import category_slices
from transactions.periods import MIN_MONTH, MONTH_PATTERN, resolve_month

from .facts import Facts, Term

SPENDING = "get_spending_by_category"
DECLINE = "decline_out_of_scope"
OFF_TOPIC = "off_topic"
SMALLTALK = "smalltalk"
# Categories past this many are grouped into one "Outras" slice, so a result stays small.
MAX_CATEGORIES = 20

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": SPENDING,
            "description": (
                "Expenses of the signed-in user in one month: the total and, for each category, "
                "its name, amount in reais and percentage of the total."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {
                        "type": "string",
                        "description": "Month as YYYY-MM. Defaults to the current month.",
                    }
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": DECLINE,
            "description": (
                "Call this when the question is not about the user's spending by category "
                f"('{OFF_TOPIC}'), or is only a greeting or thanks ('{SMALLTALK}')."
            ),
            "parameters": {
                "type": "object",
                "properties": {"kind": {"type": "string", "enum": [OFF_TOPIC, SMALLTALK]}},
                "additionalProperties": False,
            },
        },
    },
]
ALLOWED_ARGUMENTS = {SPENDING: {"month"}, DECLINE: {"kind"}}
EXAMPLE_ARGUMENTS = {SPENDING: '{"month": "2026-08"}', DECLINE: '{"kind": "off_topic"}'}


@dataclass(frozen=True)
class ToolOutcome:
    """What running a tool produced."""

    content: str  # JSON text handed back to the model
    data: dict | None = None  # the spending result, when the query worked
    facts: Facts | None = None  # what the model may cite from `data` (the guard checks it)
    decline: str | None = None  # OFF_TOPIC or SMALLTALK when the model asked to decline
    period: bool = False  # the month asked for cannot be queried at all (future or too old)


class ToolError(Exception):
    """A bad call from the model; the message goes back to it as an error result. It says what
    to fix, because the model can only correct itself with that."""


class PeriodError(ToolError):
    """A month that cannot be queried however the model writes it: nothing to correct."""


def _error(message, period=False):
    return ToolOutcome(json.dumps({"error": message}), period=period)


def _parse_arguments(name, arguments):
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments or "{}")
        except ValueError:
            example = EXAMPLE_ARGUMENTS[name]
            raise ToolError(
                f"The arguments are not valid JSON. Send an object such as {example}."
            ) from None
    if not isinstance(arguments, dict):
        raise ToolError(f"The arguments must be a JSON object, such as {EXAMPLE_ARGUMENTS[name]}.")
    unexpected = sorted(set(arguments) - ALLOWED_ARGUMENTS[name])
    if unexpected:
        accepted = ", ".join(sorted(ALLOWED_ARGUMENTS[name]))
        raise ToolError(
            f"Unexpected argument(s): {', '.join(unexpected)}. This tool accepts only: {accepted}."
        )
    return arguments


def _month_view(raw):
    """The month asked for. Strict, unlike the dashboard: a bad or future month is an error, not
    a silent fallback to the current one, so the model never believes it got a month it did not."""
    today = timezone.localdate()
    if raw is None:
        return resolve_month(None, today)
    match = MONTH_PATTERN.match(raw) if isinstance(raw, str) else None
    if not match:
        raise ToolError("The month must be a string in the format YYYY-MM, such as 2026-08.")
    try:
        first_day = date(int(match.group(1)), int(match.group(2)), 1)
    except ValueError:
        raise ToolError(
            "That month does not exist. Use YYYY-MM with a month from 01 to 12, such as 2026-08."
        ) from None
    current = today.replace(day=1)
    if first_day < MIN_MONTH:
        raise PeriodError(
            "The month must be January 2000 or later. "
            f"Use a month from {MIN_MONTH:%Y-%m} to {current:%Y-%m}."
        )
    if first_day > current:
        raise PeriodError(
            f"That month is in the future. The latest month available is {current:%Y-%m}."
        )
    return resolve_month(raw, today)


def _money(amount):
    return f"{amount:.2f}"


def _facts(total, slices):
    """The numbers of a spending result the model may cite: the total and each category."""
    return Facts(
        amounts=(
            Term(None, total),
            *(Term(s.name, Decimal(_money(s.amount))) for s in slices),
        ),
        percents=tuple(Term(s.name, Decimal(s.percent)) for s in slices),
        names=frozenset(s.name for s in slices if s.name),
    )


def _spending_by_category(user, month=None):
    view = _month_view(month)
    slices = category_slices(user, view, limit=MAX_CATEGORIES)
    total = sum((s.amount for s in slices), start=0)
    data = {
        "month": view.param,
        "label": view.label,
        "total": _money(total),
        "categories": [
            {"name": s.name, "amount": _money(s.amount), "percent": s.percent} for s in slices
        ],
    }
    facts = _facts(Decimal(data["total"]), slices)
    return ToolOutcome(json.dumps(data, ensure_ascii=False), data=data, facts=facts)


def _decline(user, kind=OFF_TOPIC):
    kind = kind if kind in (OFF_TOPIC, SMALLTALK) else OFF_TOPIC
    return ToolOutcome(json.dumps({"ok": True}), decline=kind)


HANDLERS = {SPENDING: _spending_by_category, DECLINE: _decline}


def run_tool(user, name, arguments):
    """Runs the tool `name` for `user` and returns a `ToolOutcome`; a bad call becomes an error
    result for the model, never an exception and never a query."""
    if name not in HANDLERS:
        return _error(f"Unknown tool: {name}. Available tools: {', '.join(HANDLERS)}.")
    try:
        return HANDLERS[name](user, **_parse_arguments(name, arguments))
    except PeriodError as error:
        return _error(str(error), period=True)
    except ToolError as error:
        return _error(str(error))
