from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.cache import patch_vary_headers
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import TransactionForm
from .models import Transaction, current_balance


class OwnedQuerysetMixin:
    """Restricts the queryset to the signed-in user, so another user's id is a plain 404."""

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class ModalMixin:
    """Serves the screen as a bare fragment to the modal's fetch(), and as a full page otherwise."""

    @property
    def is_modal(self):
        return self.request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # Same URL, two bodies: keep the browser from serving the fragment on a normal visit.
        patch_vary_headers(response, ("X-Requested-With",))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_modal"] = self.is_modal
        context["base_template"] = "transactions/modal_base.html" if self.is_modal else "base.html"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.is_modal:
            return JsonResponse({"location": str(self.get_success_url())})
        return response


class TransactionListView(LoginRequiredMixin, OwnedQuerysetMixin, ListView):
    template_name = "transactions/transaction_list.html"
    context_object_name = "transactions"

    def get_paginate_by(self, queryset):
        return settings.TRANSACTIONS_PER_PAGE

    def get_queryset(self):
        return super().get_queryset().order_by("-date", "-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["balance"] = current_balance(self.request.user)
        if context["is_paginated"]:
            page = context["page_obj"]
            context["page_numbers"] = list(
                page.paginator.get_elided_page_range(page.number, on_each_side=1, on_ends=1)
            )
            context["ellipsis"] = Paginator.ELLIPSIS
        return context


class TransactionCreateView(LoginRequiredMixin, ModalMixin, CreateView):
    form_class = TransactionForm
    template_name = "transactions/transaction_form.html"
    success_url = reverse_lazy("transactions:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Lançamento registrado.")
        return response


class TransactionUpdateView(LoginRequiredMixin, ModalMixin, OwnedQuerysetMixin, UpdateView):
    form_class = TransactionForm
    template_name = "transactions/transaction_form.html"
    success_url = reverse_lazy("transactions:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Lançamento atualizado.")
        return response


class TransactionDeleteView(LoginRequiredMixin, ModalMixin, OwnedQuerysetMixin, DeleteView):
    template_name = "transactions/transaction_confirm_delete.html"
    success_url = reverse_lazy("transactions:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Lançamento excluído.")
        return response
