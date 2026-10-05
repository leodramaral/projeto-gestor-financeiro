from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.cache import patch_vary_headers
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CategoryForm, TransactionForm
from .models import Category, Transaction, current_balance


class OwnedQuerysetMixin:
    """Restricts the queryset to the signed-in user, so another user's id is a plain 404."""

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class UserFormMixin:
    """Gives the form the signed-in user, who limits which categories can be picked."""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


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

    def get_selected_category(self):
        """The category in `?category=`; None when missing, not a number or not the user's."""
        raw = self.request.GET.get("category", "")
        if not raw.isdecimal():
            return None
        return Category.objects.for_user(self.request.user).filter(pk=int(raw)).first()

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category").order_by("-date", "-id")
        category = self.get_selected_category()
        return queryset.filter(category=category) if category else queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected = self.get_selected_category()
        context["balance"] = current_balance(self.request.user)
        context["categories"] = Category.objects.for_user(self.request.user)
        context["selected_category"] = selected
        context["query_prefix"] = f"category={selected.pk}&" if selected else ""
        if context["is_paginated"]:
            page = context["page_obj"]
            context["page_numbers"] = list(
                page.paginator.get_elided_page_range(page.number, on_each_side=1, on_ends=1)
            )
            context["ellipsis"] = Paginator.ELLIPSIS
        return context


class TransactionCreateView(LoginRequiredMixin, UserFormMixin, ModalMixin, CreateView):
    form_class = TransactionForm
    template_name = "transactions/transaction_form.html"
    success_url = reverse_lazy("transactions:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Lançamento registrado.")
        return response


class TransactionUpdateView(
    LoginRequiredMixin, UserFormMixin, ModalMixin, OwnedQuerysetMixin, UpdateView
):
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


class OwnedCategoryMixin:
    """Only the user's own categories: a default or someone else's is a plain 404."""

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryListView(LoginRequiredMixin, ListView):
    template_name = "transactions/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        user = self.request.user
        uses = Count("transactions", filter=Q(transactions__user=user))
        return Category.objects.for_user(user).annotate(uses=uses)


class CategoryCreateView(LoginRequiredMixin, UserFormMixin, ModalMixin, CreateView):
    form_class = CategoryForm
    template_name = "transactions/category_form.html"
    success_url = reverse_lazy("transactions:category-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Categoria criada.")
        return response


class CategoryUpdateView(
    LoginRequiredMixin, UserFormMixin, ModalMixin, OwnedCategoryMixin, UpdateView
):
    form_class = CategoryForm
    template_name = "transactions/category_form.html"
    success_url = reverse_lazy("transactions:category-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Categoria atualizada.")
        return response


class CategoryDeleteView(LoginRequiredMixin, ModalMixin, OwnedCategoryMixin, DeleteView):
    template_name = "transactions/category_confirm_delete.html"
    success_url = reverse_lazy("transactions:category-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uses"] = self.object.transactions.count()
        return context

    def form_valid(self, form):
        # Expenses of the deleted category are not lost: they move to "Outros".
        with transaction.atomic():
            self.object.transactions.update(category=Category.other())
            response = super().form_valid(form)
        messages.success(self.request, "Categoria excluída.")
        return response
