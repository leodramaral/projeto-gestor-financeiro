import pytest
from django.urls import reverse

ASIDE_MARK = "Controle suas finanças com clareza"
SPLIT_PAGES = ["accounts:login", "accounts:signup", "accounts:password_reset"]
GUEST_PAGES = [*SPLIT_PAGES, "accounts:resend"]


def render(client, name):
    response = client.get(reverse(name))
    assert response.status_code == 200
    return response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize("name", SPLIT_PAGES)
def test_split_pages_show_brand_panel(client, name):
    assert ASIDE_MARK in render(client, name)


@pytest.mark.django_db
def test_password_reset_links_back_to_login(client):
    assert reverse("accounts:login") in render(client, "accounts:password_reset")


@pytest.mark.django_db
def test_signup_links_back_to_login(client):
    assert reverse("accounts:login") in render(client, "accounts:signup")


@pytest.mark.django_db
@pytest.mark.parametrize("name", GUEST_PAGES)
def test_guest_pages_have_no_tailadmin_or_social_login(client, name):
    html = render(client, name).lower()

    assert "tailadmin" not in html
    assert "google" not in html
    assert "sign in with" not in html


@pytest.mark.django_db
def test_login_keeps_its_elements(client):
    html = render(client, "accounts:login")

    assert "Lembrar de mim" in html
    assert reverse("accounts:password_reset") in html
    assert reverse("accounts:signup") in html
