import pytest
from django.template import Context, Template
from django.urls import reverse

from accounts.templatetags.accounts_tags import initials


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Ana Souza", "AS"),
        ("ana", "A"),
        ("  ana   maria   souza ", "AM"),
        ("", ""),
    ],
)
def test_initials(name, expected):
    assert initials(name) == expected


def test_avatar_partial_renders_initials_and_size():
    user = type("U", (), {"name": "ana souza"})()
    html = Template('{% include "partials/user_avatar.html" with size="h-20 w-20" %}').render(
        Context({"user": user})
    )

    assert ">AS<" in html
    assert "h-20 w-20" in html


@pytest.mark.django_db
def test_profile_shows_own_data_only(client, make_user):
    user = make_user()
    client.force_login(user)

    content = client.get(reverse("accounts:profile")).content.decode()

    assert "Ana Souza" in content
    assert "ana@exemplo.com" in content
    assert "Sim, em" in content
    assert user.date_joined.strftime("%d/%m/%Y") in content


@pytest.mark.django_db
def test_profile_shows_unconfirmed_email(client, make_user):
    client.force_login(make_user(confirmed=False))

    content = client.get(reverse("accounts:profile")).content.decode()

    assert "Sim, em" not in content


@pytest.mark.django_db
def test_profile_redirects_anonymous_to_login(client):
    url = reverse("accounts:profile")

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f"{reverse('accounts:login')}?next={url}"


@pytest.mark.django_db
def test_profile_has_no_edit_and_no_tailadmin(client, make_user):
    client.force_login(make_user())

    content = client.get(reverse("accounts:profile")).content.decode()

    assert "<form" not in content.split("</header>")[1]
    assert "Edit" not in content
    assert "Editar" not in content
    assert "TailAdmin" not in content


@pytest.mark.django_db
def test_header_menu_has_items_and_no_loose_logout(client, make_user):
    client.force_login(make_user())

    content = client.get(reverse("transactions:list")).content.decode()

    assert f'href="{reverse("accounts:profile")}"' in content
    assert "Ver perfil" in content
    assert f'action="{reverse("accounts:logout")}"' in content
    assert 'aria-haspopup="menu"' in content
    assert "@keydown.escape" in content
    assert "@click.outside" in content


@pytest.mark.django_db
def test_logout_from_menu_ends_session(client, make_user):
    client.force_login(make_user())

    response = client.post(reverse("accounts:logout"))

    assert response.status_code == 302
    assert client.get(reverse("transactions:list")).status_code == 302
