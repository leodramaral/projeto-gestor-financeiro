from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from transactions.dashboard import build_dashboard


class HomeView(LoginRequiredMixin, TemplateView):
    """The dashboard: balance, this month's numbers and the charts."""

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dashboard"] = build_dashboard(self.request.user, timezone.localdate())
        return context
