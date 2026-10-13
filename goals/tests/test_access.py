import pytest
from django.test import Client
from django.urls import reverse

from goals.models import Goal


def routes(goal):
    return [
        ("goals:list", []),
        ("goals:create", []),
        ("goals:update", [goal.pk]),
        ("goals:progress", [goal.pk]),
        ("goals:delete", [goal.pk]),
        ("goals:complete", [goal.pk]),
        ("goals:reopen", [goal.pk]),
    ]


@pytest.mark.parametrize("method", ["get", "post"])
def test_visitor_is_sent_to_login(client, user, make_goal, method):
    goal = make_goal(user)
    for name, args in routes(goal):
        url = reverse(name, args=args)
        response = getattr(client, method)(url, {"name": "x"})
        assert response.status_code == 302, (name, method)
        assert response.url.startswith(reverse("accounts:login")), (name, method)
    goal.refresh_from_db()
    assert Goal.objects.count() == 1
    assert goal.name == "Reserva"
    assert not goal.is_completed


def test_post_without_csrf_token_is_refused(user, make_goal):
    strict = Client(enforce_csrf_checks=True)
    strict.force_login(user)
    goal = make_goal(user)
    for name in (
        "goals:create",
        "goals:update",
        "goals:progress",
        "goals:delete",
        "goals:complete",
    ):
        args = [] if name == "goals:create" else [goal.pk]
        assert strict.post(reverse(name, args=args), {"name": "x"}).status_code == 403
    assert Goal.objects.count() == 1
    assert not Goal.objects.get().is_completed
