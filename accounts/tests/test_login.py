import pytest
from django.contrib.auth import SESSION_KEY
from django.urls import reverse

from .conftest import PASSWORD

LOGIN = "accounts:login"
GENERIC = "E-mail ou senha incorretos."


@pytest.mark.django_db
def test_login_page_renders(client):
    response = client.get(reverse(LOGIN))

    assert response.status_code == 200
    assert "Lembrar de mim" in response.content.decode()


@pytest.mark.django_db
def test_valid_login_goes_to_dashboard(client, make_user):
    make_user()

    response = client.post(reverse(LOGIN), {"username": "ana@exemplo.com", "password": PASSWORD})

    assert response.status_code == 302
    assert response.url == reverse("home")
    assert SESSION_KEY in client.session


@pytest.mark.django_db
def test_email_case_does_not_matter(client, make_user):
    make_user("ana@exemplo.com")

    client.post(reverse(LOGIN), {"username": "  ANA@Exemplo.COM ", "password": PASSWORD})

    assert SESSION_KEY in client.session


@pytest.mark.django_db
def test_unknown_email_and_wrong_password_get_the_same_message(client, make_user):
    make_user()

    wrong_password = client.post(reverse(LOGIN), {"username": "ana@exemplo.com", "password": "x"})
    unknown = client.post(reverse(LOGIN), {"username": "ninguem@exemplo.com", "password": PASSWORD})

    for response in (wrong_password, unknown):
        assert response.status_code == 200
        assert GENERIC in response.content.decode()
        assert SESSION_KEY not in client.session
    assert (
        wrong_password.context["form"].non_field_errors()
        == unknown.context["form"].non_field_errors()
    )


@pytest.mark.django_db
def test_unconfirmed_account_cannot_log_in(client, make_user):
    make_user(confirmed=False)

    response = client.post(reverse(LOGIN), {"username": "ana@exemplo.com", "password": PASSWORD})

    assert response.status_code == 200
    assert SESSION_KEY not in client.session
    content = response.content.decode()
    assert "Confirme seu e-mail" in content
    assert reverse("accounts:resend") in content


@pytest.mark.django_db
def test_unconfirmed_account_with_wrong_password_gets_the_generic_message(client, make_user):
    make_user(confirmed=False)

    response = client.post(reverse(LOGIN), {"username": "ana@exemplo.com", "password": "errada"})

    assert GENERIC in response.content.decode()
    assert "Confirme seu e-mail" not in response.content.decode()


@pytest.mark.django_db
def test_inactive_account_gets_the_generic_message(client, make_user):
    make_user(is_active=False)

    response = client.post(reverse(LOGIN), {"username": "ana@exemplo.com", "password": PASSWORD})

    assert GENERIC in response.content.decode()
    assert SESSION_KEY not in client.session


@pytest.mark.django_db
def test_session_ends_with_the_browser_without_remember_me(client, make_user):
    make_user()

    response = client.post(reverse(LOGIN), {"username": "ana@exemplo.com", "password": PASSWORD})

    cookie = response.cookies["sessionid"]
    assert cookie["max-age"] == ""
    assert cookie["expires"] == ""
    assert client.session.get_expire_at_browser_close()


@pytest.mark.django_db
def test_session_persists_with_remember_me(client, make_user, settings):
    make_user()

    response = client.post(
        reverse(LOGIN), {"username": "ana@exemplo.com", "password": PASSWORD, "remember_me": "on"}
    )

    assert response.cookies["sessionid"]["max-age"] == settings.SESSION_REMEMBER_SECONDS
    assert not client.session.get_expire_at_browser_close()


@pytest.mark.django_db
def test_next_internal_is_followed_and_external_is_ignored(client, make_user):
    make_user()
    data = {"username": "ana@exemplo.com", "password": PASSWORD}

    internal = client.post(reverse(LOGIN) + "?next=/admin/", data)
    assert internal.url == "/admin/"

    client.logout()
    external = client.post(reverse(LOGIN) + "?next=https://evil.example/", data)
    assert external.url == reverse("home")


@pytest.mark.django_db
def test_signed_in_user_is_redirected_away_from_login(client, make_user):
    client.force_login(make_user())

    response = client.get(reverse(LOGIN))

    assert response.status_code == 302
    assert response.url == reverse("home")


@pytest.mark.django_db
def test_logout_requires_post(client, make_user):
    client.force_login(make_user())

    assert client.get(reverse("accounts:logout")).status_code == 405
    assert SESSION_KEY in client.session

    response = client.post(reverse("accounts:logout"))

    assert response.status_code == 302
    assert response.url == reverse(LOGIN)
    assert SESSION_KEY not in client.session
    assert client.get(reverse("home")).status_code == 302


@pytest.mark.django_db
def test_logout_post_requires_csrf_token(make_user):
    from django.test import Client

    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(make_user())

    assert csrf_client.post(reverse("accounts:logout")).status_code == 403
