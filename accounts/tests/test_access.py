import pytest
from django.urls import URLPattern, URLResolver, get_resolver, reverse

PUBLIC_PREFIXES = ("admin/", "accounts/")


def _walk(patterns, prefix=""):
    for pattern in patterns:
        route = prefix + str(pattern.pattern)
        if isinstance(pattern, URLResolver):
            yield from _walk(pattern.url_patterns, route)
        elif isinstance(pattern, URLPattern):
            yield route


def private_routes():
    return [
        route
        for route in _walk(get_resolver().url_patterns)
        if not route.startswith(PUBLIC_PREFIXES) and "<" not in route
    ]


def test_there_is_at_least_one_private_route():
    assert "" in private_routes()


@pytest.mark.django_db
@pytest.mark.parametrize("route", private_routes())
def test_private_routes_redirect_anonymous_users_to_login(client, route):
    response = client.get("/" + route)

    assert response.status_code == 302
    assert response.url == f"{reverse('accounts:login')}?next=/{route}"


@pytest.mark.django_db
def test_dashboard_shows_user_menu_with_name_and_logout(client, make_user):
    client.force_login(make_user())

    content = client.get(reverse("transactions:list")).content.decode()

    assert "Ana Souza" in content
    assert f'action="{reverse("accounts:logout")}"' in content
    assert "Sair" in content
