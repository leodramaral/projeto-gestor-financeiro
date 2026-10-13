import pytest
from django.urls import reverse

from goals.models import Goal

OWNED_ROUTES = ["goals:update", "goals:progress", "goals:delete", "goals:complete", "goals:reopen"]


def test_each_user_sees_only_their_goals(client, user, other_user, make_goal):
    make_goal(user, name="Da Ana")
    make_goal(other_user, name="Da Bia", completed=True)
    client.force_login(user)
    response = client.get(reverse("goals:list"))
    assert [g.name for g in response.context["active"]] == ["Da Ana"]
    assert response.context["completed"] == []
    assert "Da Bia" not in response.content.decode()


@pytest.mark.parametrize("name", OWNED_ROUTES)
@pytest.mark.parametrize("method", ["get", "post"])
def test_another_users_goal_is_404_and_untouched(client, user, other_user, make_goal, name, method):
    goal = make_goal(other_user, name="Da Bia", saved="10.00")
    client.force_login(user)
    data = {"name": "invadida", "target_amount": "1,00", "saved_amount": "999,00"}
    response = getattr(client, method)(reverse(name, args=[goal.pk]), data)
    # The status switches only answer POST: a GET never even looks the goal up.
    status_switch = name in ("goals:complete", "goals:reopen")
    assert response.status_code == (405 if method == "get" and status_switch else 404)
    goal.refresh_from_db()
    assert (goal.name, goal.saved_amount) == ("Da Bia", 10)
    assert not goal.is_completed
    assert Goal.objects.count() == 1


def test_a_missing_goal_is_404(logged):
    assert logged.get(reverse("goals:update", args=[999999])).status_code == 404
