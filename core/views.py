from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView


class HomeView(LoginRequiredMixin, RedirectView):
    """The start page is the transaction list."""

    pattern_name = "transactions:list"
