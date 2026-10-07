from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from transactions import dashboard
from transactions.periods import first_transaction_month, resolve_month

TABS = (
    ("overview", "Visão geral", "home"),
    ("categories", "Categorias", "dashboard_categories"),
    ("flow", "Fluxo e saldo", "dashboard_flow"),
    ("transactions", "Lançamentos", "dashboard_transactions"),
)


def month_url(url_name, month):
    """`url_name` with the `month` query, so the chosen month survives every link."""
    return f"{reverse(url_name)}?month={month.strftime('%Y-%m')}"


class DashboardTabView(LoginRequiredMixin, TemplateView):
    """Base of the dashboard tabs: resolves the month once and builds the selector and the tabs.

    Subclasses set `tab` and `template_name` and return what they show from `tab_context`.
    A user without transactions gets the empty state: no month selector, tabs or charts.
    """

    tab = None

    def tab_context(self, user, month):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        first_month = first_transaction_month(user)
        month = resolve_month(self.request.GET.get("month"), timezone.localdate(), first_month)
        context.update(
            dashboard_tab=self.tab,
            has_transactions=first_month is not None,
            month=month,
            tabs=[
                {
                    "key": key,
                    "label": label,
                    "url": month_url(url_name, month.start),
                    "active": key == self.tab,
                }
                for key, label, url_name in TABS
            ],
            previous_url=month_url(self.request.resolver_match.url_name, month.previous)
            if month.has_previous
            else None,
            next_url=month_url(self.request.resolver_match.url_name, month.next)
            if month.next
            else None,
            month_param=month.param,
        )
        if first_month is not None:
            context.update(self.tab_context(user, month))
        return context


class OverviewView(DashboardTabView):
    """Every number and chart of the month, with a link to each segment's tab."""

    tab = "overview"
    template_name = "core/home.html"

    def tab_context(self, user, month):
        overview = dashboard.build_dashboard(user, month)
        return {"dashboard": overview, "chart_data": overview.chart_data}


class CategoriesView(DashboardTabView):
    tab = "categories"
    template_name = "core/categories.html"

    def tab_context(self, user, month):
        slices = dashboard.category_slices(user, month)
        return {
            "categories": slices,
            "expense_total": sum(s.amount for s in slices),
            "chart_data": dashboard.chart_data(categories=slices),
        }


class FlowView(DashboardTabView):
    tab = "flow"
    template_name = "core/flow.html"

    def tab_context(self, user, month):
        summary = dashboard.build_summary(user, month)
        days = dashboard.daily_series(user, month, summary.opening)
        return {"summary": summary, "chart_data": dashboard.chart_data(days=days)}


class TransactionsTabView(DashboardTabView):
    tab = "transactions"
    template_name = "core/transactions.html"

    def tab_context(self, user, month):
        return {"transactions": dashboard.month_transactions(user, month)}
