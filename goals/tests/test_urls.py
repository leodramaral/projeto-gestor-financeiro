import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    ("name", "args", "path"),
    [
        ("goals:list", [], "/goals/"),
        ("goals:create", [], "/goals/new/"),
        ("goals:update", [7], "/goals/7/edit/"),
        ("goals:progress", [7], "/goals/7/progress/"),
        ("goals:delete", [7], "/goals/7/delete/"),
        ("goals:complete", [7], "/goals/7/complete/"),
        ("goals:reopen", [7], "/goals/7/reopen/"),
    ],
)
def test_routes_resolve(name, args, path):
    assert reverse(name, args=args) == path
