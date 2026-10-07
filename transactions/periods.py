"""The month the dashboard shows: resolved once from the URL and shared by every tab."""

import re
from dataclasses import dataclass
from datetime import date

from django.db.models import Min
from django.utils.dates import MONTHS

from .models import Transaction

MONTH_PATTERN = re.compile(r"^(\d{4})-(\d{2})$")


def shift_month(day, delta):
    """The first day of the month `delta` months away from the month of `day`."""
    index = day.year * 12 + (day.month - 1) + delta
    return date(index // 12, index % 12 + 1, 1)


def _label(day):
    return f"{str(MONTHS[day.month]).lower()} de {day.year}"


@dataclass(frozen=True)
class MonthView:
    """A calendar month plus the neighbours the month selector links to."""

    start: date  # first day of the month
    end: date  # last day of the month, inclusive
    previous: date  # first day of the month before
    next: date | None  # first day of the month after; None on the current month
    has_previous: bool  # False on the month of the user's first transaction

    @property
    def param(self):
        return self.start.strftime("%Y-%m")

    @property
    def label(self):
        return _label(self.start)

    @property
    def previous_label(self):
        return _label(self.previous)

    @property
    def day_before(self):
        """The last day of the previous month."""
        return date.fromordinal(self.start.toordinal() - 1)


def _parse_month(raw, current):
    """The first day of the month in `raw` ("YYYY-MM"), or `current` when it is not usable."""
    match = MONTH_PATTERN.match(raw or "")
    if not match:
        return current
    try:
        month = date(int(match.group(1)), int(match.group(2)), 1)
    except ValueError:
        return current
    return min(month, current)


def resolve_month(raw, today, first_month=None):
    """The month to show for `raw` (the `month` query value), with `today` as the upper bound.

    A missing, malformed, non-existent or future month falls back to the current one; a month
    before `first_month` (the month of the first transaction) is raised to it.
    """
    current = today.replace(day=1)
    start = _parse_month(raw, current)
    if first_month and start < first_month:
        start = first_month
    following = shift_month(start, 1)
    return MonthView(
        start=start,
        end=date.fromordinal(following.toordinal() - 1),
        previous=shift_month(start, -1),
        next=following if start < current else None,
        has_previous=start > (first_month or current),
    )


def first_transaction_month(user):
    """The first day of the month of the user's oldest transaction, or None without any."""
    oldest = Transaction.objects.filter(user=user).aggregate(oldest=Min("date"))["oldest"]
    return oldest.replace(day=1) if oldest else None
