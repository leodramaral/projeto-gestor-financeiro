from datetime import timedelta
from decimal import Decimal

from django.urls import reverse

from goals.models import Goal
from transactions.models import Transaction, current_balance

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


def payload(**overrides):
    data = {"name": "Reserva", "target_amount": "500,00", "saved_amount": "0,00", "deadline": ""}
    data.update(overrides)
    return data


def test_create_with_deadline(logged, user, future):
    response = logged.post(
        reverse("goals:create"), payload(deadline=future.isoformat()), follow=True
    )
    goal = Goal.objects.get()
    assert (goal.user, goal.name, goal.target_amount) == (user, "Reserva", Decimal("500.00"))
    assert goal.deadline == future
    assert goal.saved_amount == 0
    assert not goal.is_completed
    assert "Meta criada." in response.content.decode()


def test_create_without_deadline(logged):
    logged.post(reverse("goals:create"), payload())
    assert Goal.objects.get().deadline is None


def test_invalid_create_saves_nothing_and_shows_the_error(logged):
    response = logged.post(reverse("goals:create"), payload(target_amount="0,00"))
    assert response.status_code == 200
    assert "O valor deve ser maior que zero." in response.content.decode()
    assert not Goal.objects.exists()


def test_create_as_modal_answers_with_the_location(logged):
    response = logged.post(reverse("goals:create"), payload(), **AJAX)
    assert response.json() == {"location": reverse("goals:list")}


def test_modal_get_is_a_fragment_and_page_get_is_full(logged):
    fragment = logged.get(reverse("goals:create"), **AJAX).content.decode()
    page = logged.get(reverse("goals:create")).content.decode()
    assert "<aside" not in fragment
    assert "<aside" in page


def test_progress_does_not_touch_transactions_or_balance(logged, user, make_goal):
    goal = make_goal(user, target="500.00")
    before = current_balance(user)
    logged.post(reverse("goals:progress", args=[goal.pk]), {"saved_amount": "200,00"})
    goal.refresh_from_db()
    assert goal.saved_amount == Decimal("200.00")
    assert not Transaction.objects.exists()
    assert current_balance(user) == before


def test_negative_progress_is_refused_and_keeps_the_value(logged, user, make_goal):
    goal = make_goal(user, saved="40.00")
    response = logged.post(reverse("goals:progress", args=[goal.pk]), {"saved_amount": "-5,00"})
    goal.refresh_from_db()
    assert goal.saved_amount == Decimal("40.00")
    assert "O valor guardado não pode ser negativo." in response.content.decode()


def test_progress_on_overdue_goal_is_saved(logged, user, make_goal, today):
    goal = make_goal(user, deadline=today - timedelta(days=3))
    logged.post(
        reverse("goals:update", args=[goal.pk]),
        payload(saved_amount="50,00", deadline=goal.deadline.isoformat()),
    )
    goal.refresh_from_db()
    assert goal.saved_amount == Decimal("50.00")


def test_edit_updates_the_target(logged, user, make_goal):
    goal = make_goal(user, target="500.00", saved="250.00")
    logged.post(
        reverse("goals:update", args=[goal.pk]),
        payload(target_amount="1.000,00", saved_amount="250,00"),
    )
    goal.refresh_from_db()
    assert goal.target_amount == Decimal("1000.00")
    assert goal.progress_percent == 25


def test_delete_asks_first_and_only_removes_on_post(logged, user, make_goal):
    goal = make_goal(user)
    page = logged.get(reverse("goals:delete", args=[goal.pk]))
    assert "Tem certeza" in page.content.decode()
    assert Goal.objects.count() == 1
    logged.post(reverse("goals:delete", args=[goal.pk]))
    assert not Goal.objects.exists()


def test_delete_keeps_transactions_and_balance(logged, user, make_goal):
    Transaction.objects.create(
        user=user, kind="income", amount=100, date="2026-10-01", description="x"
    )
    goal = make_goal(user)
    logged.post(reverse("goals:delete", args=[goal.pk]))
    assert Transaction.objects.count() == 1
    assert current_balance(user) == 100


def test_complete_then_reopen(logged, user, make_goal):
    goal = make_goal(user, saved="10.00")
    response = logged.post(reverse("goals:complete", args=[goal.pk]), follow=True)
    goal.refresh_from_db()
    assert goal.is_completed
    assert goal.progress_percent == 2  # still reflects what was really saved
    assert "Meta concluída." in response.content.decode()
    response = logged.post(reverse("goals:reopen", args=[goal.pk]), follow=True)
    goal.refresh_from_db()
    assert not goal.is_completed
    assert "Meta reaberta." in response.content.decode()


def test_complete_twice_keeps_the_first_moment(logged, user, make_goal):
    goal = make_goal(user)
    logged.post(reverse("goals:complete", args=[goal.pk]))
    goal.refresh_from_db()
    first = goal.completed_at
    logged.post(reverse("goals:complete", args=[goal.pk]))
    goal.refresh_from_db()
    assert goal.completed_at == first


def test_status_routes_need_post(logged, user, make_goal):
    goal = make_goal(user)
    assert logged.get(reverse("goals:complete", args=[goal.pk])).status_code == 405
    goal.complete()
    assert logged.get(reverse("goals:reopen", args=[goal.pk])).status_code == 405
    goal.refresh_from_db()
    assert goal.is_completed


def test_reopen_of_an_active_goal_changes_nothing(logged, user, make_goal):
    goal = make_goal(user)
    logged.post(reverse("goals:reopen", args=[goal.pk]))
    goal.refresh_from_db()
    assert not goal.is_completed


def test_list_separates_active_and_completed(logged, user, make_goal):
    make_goal(user, name="Em aberto")
    make_goal(user, name="Feita", completed=True)
    response = logged.get(reverse("goals:list"))
    assert [g.name for g in response.context["active"]] == ["Em aberto"]
    assert [g.name for g in response.context["completed"]] == ["Feita"]
    html = response.content.decode()
    assert "1 meta em andamento" in html
    assert "1 meta concluída" in html


def test_list_subtitles_use_the_plural(logged, user, make_goal):
    for i in range(2):
        make_goal(user, name=f"A{i}")
        make_goal(user, name=f"C{i}", completed=True)
    html = logged.get(reverse("goals:list")).content.decode()
    assert "2 metas em andamento" in html
    assert "2 metas concluídas" in html


def test_list_orders_active_by_deadline_with_open_ones_last(logged, user, make_goal, today):
    make_goal(user, name="Sem prazo")
    make_goal(user, name="Longe", deadline=today + timedelta(days=60))
    make_goal(user, name="Perto", deadline=today + timedelta(days=3))
    response = logged.get(reverse("goals:list"))
    assert [g.name for g in response.context["active"]] == ["Perto", "Longe", "Sem prazo"]


def test_overdue_goal_is_flagged(logged, user, make_goal, today):
    make_goal(user, deadline=today - timedelta(days=2))
    assert "Atrasada" in logged.get(reverse("goals:list")).content.decode()


def test_no_overdue_flag_when_on_time(logged, user, make_goal, future):
    make_goal(user, deadline=future)
    assert "Atrasada" not in logged.get(reverse("goals:list")).content.decode()


def test_empty_state(logged):
    html = logged.get(reverse("goals:list")).content.decode()
    assert "Você ainda não tem metas." in html
    assert "Criar a primeira meta" in html
    assert "Concluídas" not in html


def test_only_active_goals_hides_the_completed_section(logged, user, make_goal):
    make_goal(user)
    assert "Concluídas" not in logged.get(reverse("goals:list")).content.decode()


def test_only_completed_goals_shows_a_notice_for_active(logged, user, make_goal):
    make_goal(user, completed=True)
    html = logged.get(reverse("goals:list")).content.decode()
    assert "Nenhuma meta ativa." in html
    assert "Concluídas" in html


def test_progress_bar_is_accessible_and_capped(logged, user, make_goal):
    make_goal(user, name="Meta", target="500.00", saved="800.00")
    html = logged.get(reverse("goals:list")).content.decode()
    assert 'role="progressbar"' in html
    assert 'aria-valuenow="100"' in html
    assert "width: 100%" in html
    assert "R$ 800,00" in html


def test_empty_progress_bar_is_zero(logged, user, make_goal):
    make_goal(user)
    html = logged.get(reverse("goals:list")).content.decode()
    assert 'aria-valuenow="0"' in html
    assert "width: 0%" in html


def test_goal_without_deadline_shows_the_chip(logged, user, make_goal):
    make_goal(user)
    assert "Sem prazo" in logged.get(reverse("goals:list")).content.decode()


def test_row_menu_has_the_actions(logged, user, make_goal):
    goal = make_goal(user)
    html = logged.get(reverse("goals:list")).content.decode()
    for text in ("Registrar progresso", "Editar", "Marcar como concluída", "Excluir"):
        assert text in html
    assert reverse("goals:complete", args=[goal.pk]) in html


def test_completed_row_offers_reopen(logged, user, make_goal):
    goal = make_goal(user, completed=True)
    html = logged.get(reverse("goals:list")).content.decode()
    assert reverse("goals:reopen", args=[goal.pk]) in html
    assert "Marcar como concluída" not in html
