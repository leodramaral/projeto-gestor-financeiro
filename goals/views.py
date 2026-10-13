from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from transactions.views import ModalMixin

from .forms import GoalForm, GoalProgressForm
from .models import Goal


def _plural(count, word):
    return word if count == 1 else f"{word}s"


class OwnedGoalMixin:
    """Restricts the queryset to the signed-in user, so another user's id is a plain 404."""

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)


class GoalListView(LoginRequiredMixin, ListView):
    template_name = "goals/goal_list.html"
    context_object_name = "goals"

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goals = self.object_list
        active, completed = list(goals.active()), list(goals.completed())
        context["active"] = active
        context["completed"] = completed
        context["active_subtitle"] = f"{len(active)} {_plural(len(active), 'meta')} em andamento"
        context["completed_subtitle"] = (
            f"{len(completed)} {_plural(len(completed), 'meta')} "
            f"{_plural(len(completed), 'concluída')}"
        )
        return context


class GoalCreateView(LoginRequiredMixin, ModalMixin, CreateView):
    form_class = GoalForm
    template_name = "goals/goal_form.html"
    success_url = reverse_lazy("goals:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Meta criada.")
        return response


class GoalUpdateView(LoginRequiredMixin, ModalMixin, OwnedGoalMixin, UpdateView):
    form_class = GoalForm
    template_name = "goals/goal_form.html"
    success_url = reverse_lazy("goals:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Meta atualizada.")
        return response


class GoalProgressView(LoginRequiredMixin, ModalMixin, OwnedGoalMixin, UpdateView):
    form_class = GoalProgressForm
    template_name = "goals/goal_progress_form.html"
    success_url = reverse_lazy("goals:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Progresso registrado.")
        return response


class GoalDeleteView(LoginRequiredMixin, ModalMixin, OwnedGoalMixin, DeleteView):
    template_name = "goals/goal_confirm_delete.html"
    success_url = reverse_lazy("goals:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Meta excluída.")
        return response


class GoalStatusView(LoginRequiredMixin, OwnedGoalMixin, View):
    """POST-only switch between active and completed; subclasses say which way."""

    http_method_names = ["post"]
    message = ""

    def change(self, goal):
        raise NotImplementedError

    def post(self, request, pk):
        goal = get_object_or_404(self.get_queryset(), pk=pk)
        self.change(goal)
        messages.success(request, self.message)
        return redirect("goals:list")


class GoalCompleteView(GoalStatusView):
    message = "Meta concluída."

    def change(self, goal):
        if not goal.is_completed:
            goal.complete()


class GoalReopenView(GoalStatusView):
    message = "Meta reaberta."

    def change(self, goal):
        if goal.is_completed:
            goal.reopen()
