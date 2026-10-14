"""Numbers behind the dashboard: everything is computed from the signed-in user's transactions
within one calendar month (see `periods.MonthView`)."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from .appearance import COLOR_BY_KEY, DEFAULT_COLOR
from .models import ZERO, Transaction

TOP_CATEGORIES = 5
RECENT_COUNT = 5
OTHER_SLICES_NAME = "Outras"
WEEK_DAYS = 7


@dataclass(frozen=True)
class DayPoint:
    label: str  # day of the month
    income: Decimal
    expense: Decimal
    balance: Decimal  # at the end of the day


@dataclass(frozen=True)
class WeekPoint:
    """A block of up to 7 days from day 1 of the month; the last one holds the remaining days."""

    label: str  # "Sem 1"
    span: str  # "1–7", or a single day when the block has only one
    income: Decimal
    expense: Decimal


@dataclass(frozen=True)
class LowestBalance:
    """The lowest end-of-day balance of the month (the earliest day wins a tie)."""

    day: date
    balance: Decimal


@dataclass(frozen=True)
class CategorySlice:
    name: str
    color: str  # key from `appearance.COLORS`
    amount: Decimal
    percent: int


@dataclass(frozen=True)
class Summary:
    """The month in numbers: opening balance + income - expense = closing balance."""

    opening: Decimal
    income: Decimal
    expense: Decimal
    closing: Decimal
    status: str  # of the closing balance: "negative", "zero" or "positive"
    previous_income: Decimal
    previous_expense: Decimal
    income_change: int | None
    expense_change: int | None
    savings_rate: Decimal | None


@dataclass(frozen=True)
class Dashboard:
    """What the overview tab shows."""

    summary: Summary
    days: list
    categories: list
    recent: list
    largest_expense: Transaction | None
    lowest: LowestBalance

    @property
    def chart_data(self):
        return chart_data(days=self.days, categories=self.categories)


def chart_data(days=None, categories=None):
    """What the charts draw, as plain JSON types (amounts as numbers with two decimals).

    Only the keys of the parts a page shows are present.
    """
    data = {}
    if days is not None:
        data["days"] = [d.label for d in days]
        data["income"] = [float(d.income) for d in days]
        data["expense"] = [float(d.expense) for d in days]
        data["balance"] = [float(d.balance) for d in days]
        weeks = weekly_series(days)
        data["weeks"] = {
            "labels": [[w.label, w.span] for w in weeks],
            "income": [float(w.income) for w in weeks],
            "expense": [float(w.expense) for w in weeks],
        }
        data["lowest"] = lowest_index(days)
    if categories is not None:
        data["categories"] = [
            {
                "name": s.name,
                "amount": float(s.amount),
                "light": COLOR_BY_KEY[s.color].fill,
                "dark": COLOR_BY_KEY[s.color].fill_dark,
            }
            for s in categories
        ]
    return data


def _net(queryset):
    """Incomes minus expenses of a queryset of transactions."""
    totals = _totals(queryset)
    return totals["income"] - totals["expense"]


def _totals(queryset):
    return queryset.aggregate(
        income=Coalesce(Sum("amount", filter=Q(kind=Transaction.Kind.INCOME)), ZERO),
        expense=Coalesce(Sum("amount", filter=Q(kind=Transaction.Kind.EXPENSE)), ZERO),
    )


def _in_month(user, start, end):
    return Transaction.objects.filter(user=user, date__gte=start, date__lte=end)


def opening_balance(user, start):
    """Incomes minus expenses of everything dated before `start`."""
    return _net(Transaction.objects.filter(user=user, date__lt=start))


def _change(current, previous):
    """Percent change from `previous` to `current`; None when there is nothing to compare to."""
    if not previous:
        return None
    return int(((current - previous) / previous * 100).quantize(Decimal("1"), ROUND_HALF_UP))


def _savings_rate(income, expense):
    if not income:
        return None
    return ((income - expense) / income * 100).quantize(Decimal("0.1"), ROUND_HALF_UP)


def _status(balance):
    if balance < 0:
        return "negative"
    return "positive" if balance > 0 else "zero"


def build_summary(user, month):
    """Opening and closing balance, totals and changes against the month before."""
    current = _totals(_in_month(user, month.start, month.end))
    previous_start = month.previous
    previous = _totals(_in_month(user, previous_start, month.start - timedelta(days=1)))
    opening = opening_balance(user, month.start)
    closing = opening + current["income"] - current["expense"]
    return Summary(
        opening=opening,
        income=current["income"],
        expense=current["expense"],
        closing=closing,
        status=_status(closing),
        previous_income=previous["income"],
        previous_expense=previous["expense"],
        income_change=_change(current["income"], previous["income"]),
        expense_change=_change(current["expense"], previous["expense"]),
        savings_rate=_savings_rate(current["income"], current["expense"]),
    )


def daily_series(user, month, opening):
    """One point per day of the month; days without transactions repeat the balance."""
    rows = (
        _in_month(user, month.start, month.end)
        .values("date", "kind")
        .annotate(total=Sum("amount"))
        .order_by()
    )
    flow = {(row["date"], row["kind"]): row["total"] for row in rows}
    balance = opening
    points = []
    for offset in range(month.end.day):
        day = month.start + timedelta(days=offset)
        income = flow.get((day, Transaction.Kind.INCOME), ZERO)
        expense = flow.get((day, Transaction.Kind.EXPENSE), ZERO)
        balance += income - expense
        points.append(DayPoint(str(day.day), income, expense, balance))
    return points


def weekly_series(days):
    """The daily points summed in blocks of `WEEK_DAYS`, so the blocks add up to the month."""
    weeks = []
    for number, first in enumerate(range(0, len(days), WEEK_DAYS), start=1):
        block = days[first : first + WEEK_DAYS]
        first_day, last_day = block[0].label, block[-1].label
        weeks.append(
            WeekPoint(
                label=f"Sem {number}",
                span=first_day if first_day == last_day else f"{first_day}–{last_day}",
                income=sum((d.income for d in block), ZERO),
                expense=sum((d.expense for d in block), ZERO),
            )
        )
    return weeks


def lowest_index(days):
    """Index of the day with the lowest end-of-day balance (the earliest one on a tie)."""
    return min(range(len(days)), key=lambda i: (days[i].balance, i))


def lowest_balance(days, month):
    """The lowest end-of-day balance of the month and its date."""
    index = lowest_index(days)
    return LowestBalance(month.start + timedelta(days=index), days[index].balance)


def largest_expense(user, month):
    """The biggest expense of the month (the newest one on a tie), or None without expenses."""
    return (
        _in_month(user, month.start, month.end)
        .filter(kind=Transaction.Kind.EXPENSE)
        .order_by("-amount", "-date", "-id")
        .first()
    )


def category_slices(user, month, limit=None):
    """Expenses of the month by category, largest first.

    With `limit`, the categories past it are grouped into one "Outras" slice.
    """
    rows = list(
        _in_month(user, month.start, month.end)
        .filter(kind=Transaction.Kind.EXPENSE)
        .values("category_id", "category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total", "category__name")
    )
    total = sum((row["total"] for row in rows), ZERO)
    if not total:
        return []
    slices = [(row["category__name"], row["category__color"], row["total"]) for row in rows]
    if limit is not None and len(rows) > limit:
        rest = sum((row["total"] for row in rows[limit:]), ZERO)
        slices = slices[:limit] + [(OTHER_SLICES_NAME, DEFAULT_COLOR, rest)]
    return [
        CategorySlice(
            name,
            color if color in COLOR_BY_KEY else DEFAULT_COLOR,
            amount,
            int((amount / total * 100).quantize(Decimal("1"), ROUND_HALF_UP)),
        )
        for name, color, amount in slices
    ]


def month_transactions(user, month, limit=None):
    """The month's transactions in the same order as the list (newest first)."""
    queryset = _in_month(user, month.start, month.end).select_related("category")
    queryset = queryset.order_by("-date", "-id")
    return list(queryset[:limit]) if limit else list(queryset)


def build_dashboard(user, month):
    """Everything the overview tab shows for `user` in `month`."""
    summary = build_summary(user, month)
    days = daily_series(user, month, summary.opening)
    return Dashboard(
        summary=summary,
        days=days,
        categories=category_slices(user, month, limit=TOP_CATEGORIES),
        recent=month_transactions(user, month, limit=RECENT_COUNT),
        largest_expense=largest_expense(user, month),
        lowest=lowest_balance(days, month),
    )
