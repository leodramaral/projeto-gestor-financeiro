"""Numbers behind the dashboard: everything is computed from the signed-in user's transactions."""

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Q, Sum
from django.db.models.functions import Coalesce, TruncMonth
from django.utils.dates import MONTHS_3

from .appearance import COLOR_BY_KEY, DEFAULT_COLOR
from .models import ZERO, Transaction, current_balance

WINDOW_MONTHS = 6
TOP_CATEGORIES = 5
RECENT_COUNT = 5
OTHER_SLICES_NAME = "Outras"


@dataclass(frozen=True)
class MonthPoint:
    label: str
    income: Decimal
    expense: Decimal
    balance: Decimal  # at the end of the month


@dataclass(frozen=True)
class CategorySlice:
    name: str
    color: str  # key from `appearance.COLORS`
    amount: Decimal
    percent: int


@dataclass(frozen=True)
class Dashboard:
    balance: Decimal
    status: str  # "negative", "zero" or "positive"
    has_transactions: bool
    month_income: Decimal
    month_expense: Decimal
    income_change: int | None
    expense_change: int | None
    savings_rate: Decimal | None
    categories: list
    months: list
    recent: list

    @property
    def chart_data(self):
        """What the charts draw, as plain JSON types (amounts as numbers with two decimals)."""
        return {
            "months": [m.label for m in self.months],
            "income": [float(m.income) for m in self.months],
            "expense": [float(m.expense) for m in self.months],
            "balance": [float(m.balance) for m in self.months],
            "categories": [
                {
                    "name": s.name,
                    "amount": float(s.amount),
                    "light": COLOR_BY_KEY[s.color].fill,
                    "dark": COLOR_BY_KEY[s.color].fill_dark,
                }
                for s in self.categories
            ],
        }


def shift_month(day, delta):
    """The first day of the month `delta` months away from the month of `day`."""
    index = day.year * 12 + (day.month - 1) + delta
    return date(index // 12, index % 12 + 1, 1)


def _net(queryset):
    """Incomes minus expenses of a queryset of transactions."""
    totals = queryset.aggregate(
        income=Coalesce(Sum("amount", filter=Q(kind=Transaction.Kind.INCOME)), ZERO),
        expense=Coalesce(Sum("amount", filter=Q(kind=Transaction.Kind.EXPENSE)), ZERO),
    )
    return totals["income"] - totals["expense"]


def _monthly_flow(user, first_month):
    """{(month start, kind): total} from `first_month` to the end of the month of `today`."""
    last_month_end = shift_month(first_month, WINDOW_MONTHS)
    rows = (
        Transaction.objects.filter(user=user, date__gte=first_month, date__lt=last_month_end)
        .annotate(month=TruncMonth("date"))
        .values("month", "kind")
        .annotate(total=Sum("amount"))
        .order_by()
    )
    return {(row["month"], row["kind"]): row["total"] for row in rows}


def _month_points(user, today):
    first_month = shift_month(today, -(WINDOW_MONTHS - 1))
    flow = _monthly_flow(user, first_month)
    balance = _net(Transaction.objects.filter(user=user, date__lt=first_month))
    points = []
    for offset in range(WINDOW_MONTHS):
        month = shift_month(first_month, offset)
        income = flow.get((month, Transaction.Kind.INCOME), ZERO)
        expense = flow.get((month, Transaction.Kind.EXPENSE), ZERO)
        balance += income - expense
        points.append(MonthPoint(str(MONTHS_3[month.month]), income, expense, balance))
    return points


def _category_slices(user, today):
    month_start = today.replace(day=1)
    rows = list(
        Transaction.objects.filter(
            user=user,
            kind=Transaction.Kind.EXPENSE,
            date__gte=month_start,
            date__lt=shift_month(month_start, 1),
        )
        .values("category_id", "category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total", "category__name")
    )
    total = sum((row["total"] for row in rows), ZERO)
    if not total:
        return []
    slices = [
        (row["category__name"], row["category__color"], row["total"])
        for row in rows[:TOP_CATEGORIES]
    ]
    rest = sum((row["total"] for row in rows[TOP_CATEGORIES:]), ZERO)
    if rest:
        slices.append((OTHER_SLICES_NAME, DEFAULT_COLOR, rest))
    return [
        CategorySlice(
            name,
            color if color in COLOR_BY_KEY else DEFAULT_COLOR,
            amount,
            int((amount / total * 100).quantize(Decimal("1"), ROUND_HALF_UP)),
        )
        for name, color, amount in slices
    ]


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


def build_dashboard(user, today):
    """Everything the dashboard shows for `user`, with `today` deciding the current month."""
    months = _month_points(user, today)
    current, previous = months[-1], months[-2]
    balance = current_balance(user)
    recent = list(Transaction.objects.filter(user=user).select_related("category")[:RECENT_COUNT])
    return Dashboard(
        balance=balance,
        status=_status(balance),
        has_transactions=bool(recent),
        month_income=current.income,
        month_expense=current.expense,
        income_change=_change(current.income, previous.income),
        expense_change=_change(current.expense, previous.expense),
        savings_rate=_savings_rate(current.income, current.expense),
        categories=_category_slices(user, today),
        months=months,
        recent=recent,
    )
