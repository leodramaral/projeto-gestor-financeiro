"""Numbers behind the dashboard: everything is computed from the signed-in user's transactions
within one calendar month (see `periods.MonthView`)."""

from dataclasses import dataclass
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from .appearance import COLOR_BY_KEY, DEFAULT_COLOR
from .models import ZERO, Transaction

TOP_CATEGORIES = 5
RECENT_COUNT = 5
OTHER_SLICES_NAME = "Outras"


@dataclass(frozen=True)
class DayPoint:
    label: str  # day of the month
    income: Decimal
    expense: Decimal
    balance: Decimal  # at the end of the day


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
    return Dashboard(
        summary=summary,
        days=daily_series(user, month, summary.opening),
        categories=category_slices(user, month, limit=TOP_CATEGORIES),
        recent=month_transactions(user, month, limit=RECENT_COUNT),
    )
