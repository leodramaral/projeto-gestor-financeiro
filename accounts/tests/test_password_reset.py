import re
from datetime import timedelta
from smtplib import SMTPException
from unittest.mock import patch

import pytest
from django.contrib.auth import SESSION_KEY
from django.core import mail
from django.test import Client
from django.urls import reverse

from accounts import throttle
from accounts.models import LoginThrottle
from accounts.tokens import email_confirmation_token, password_reset_token

from .conftest import PASSWORD, confirmation_path

REQUEST = "accounts:password_reset"
NEW_PASSWORD = "outra-senha-forte-456"
INVALID_TITLE = "Link inválido, expirado ou já utilizado"


def reset_path(message=None):
    message = message or mail.outbox[-1]
    match = re.search(r"http://testserver(/accounts/password-reset/[^\s<\"]+)", message.body)
    return match.group(1)


def ask_reset(client, email="ana@exemplo.com"):
    return client.post(reverse(REQUEST), {"email": email})


def open_link(client, path):
    """Follow the link, then the redirect Django makes to hide the token from the URL."""
    response = client.get(path, follow=True)
    return response


def submit_new_password(client, path, password=NEW_PASSWORD, confirm=None):
    response = open_link(client, path)
    return client.post(
        response.redirect_chain[-1][0] if response.redirect_chain else path,
        {"new_password1": password, "new_password2": confirm or password},
    )


# --- token generator -------------------------------------------------------------------------


@pytest.mark.django_db
def test_token_is_valid_then_voided_by_a_password_change(make_user):
    user = make_user()
    token = password_reset_token.make_token(user)
    assert password_reset_token.check_token(user, token)

    user.set_password(NEW_PASSWORD)
    user.save()

    assert not password_reset_token.check_token(user, token)


@pytest.mark.django_db
def test_token_expires_after_its_own_timeout(make_user, settings):
    settings.PASSWORD_RESET_LINK_TIMEOUT = 3600
    user = make_user()
    token = password_reset_token.make_token(user)
    now = password_reset_token._now()

    # Still inside the (longer) confirmation lifetime, but past the reset one.
    with patch.object(
        type(password_reset_token), "_now", return_value=now + timedelta(seconds=3601)
    ):
        assert not password_reset_token.check_token(user, token)
    with patch.object(
        type(password_reset_token), "_now", return_value=now + timedelta(seconds=3599)
    ):
        assert password_reset_token.check_token(user, token)


@pytest.mark.django_db
def test_confirmation_and_reset_tokens_are_not_interchangeable(make_user):
    user = make_user(confirmed=False)

    assert not password_reset_token.check_token(user, email_confirmation_token.make_token(user))
    assert not email_confirmation_token.check_token(user, password_reset_token.make_token(user))


# --- email ----------------------------------------------------------------------------------


@pytest.mark.django_db
def test_email_has_absolute_link_and_validity(client, make_user, settings):
    settings.SITE_URL = "https://app.exemplo.com"
    make_user()

    ask_reset(client)

    message = mail.outbox[0]
    assert message.to == ["ana@exemplo.com"]
    assert "https://app.exemplo.com/accounts/password-reset/" in message.body
    assert "60 minutos" in message.body
    assert "https://app.exemplo.com/accounts/password-reset/" in message.alternatives[0].content


# --- request ---------------------------------------------------------------------------------


@pytest.mark.django_db
def test_request_page_renders_and_login_links_to_it(client):
    assert client.get(reverse(REQUEST)).status_code == 200

    login = client.get(reverse("accounts:login")).content.decode()

    assert "Esqueci minha senha" in login
    assert reverse(REQUEST) in login


@pytest.mark.django_db
def test_confirmed_account_receives_the_link(client, make_user):
    make_user()

    response = ask_reset(client, "  ANA@Exemplo.COM ")

    assert response.status_code == 302
    assert len(mail.outbox) == 1


@pytest.mark.django_db
@pytest.mark.parametrize("kind", ["unknown", "unconfirmed", "inactive"])
def test_no_email_and_same_answer_for_accounts_without_the_right(client, make_user, kind):
    make_user(confirmed=kind != "unconfirmed", is_active=kind != "inactive")
    email = "ninguem@exemplo.com" if kind == "unknown" else "ana@exemplo.com"
    baseline = ask_reset(Client(), "ana@exemplo.com")
    mail.outbox.clear()

    response = ask_reset(client, email)

    assert mail.outbox == []
    assert response.status_code == baseline.status_code
    assert response.url == baseline.url


@pytest.mark.django_db
def test_done_page_is_identical_whatever_the_email(client, make_user):
    make_user()
    pages = []
    for email in ("ana@exemplo.com", "ninguem@exemplo.com"):
        response = ask_reset(client, email)
        pages.append(client.get(response.url).content)

    assert pages[0] == pages[1]
    assert "Se houver uma conta" in pages[0].decode()


@pytest.mark.django_db
def test_smtp_failure_does_not_change_the_answer(client, make_user):
    make_user()
    with patch("accounts.views.send_password_reset_email", side_effect=SMTPException):
        response = ask_reset(client)

    assert response.status_code == 302
    assert response.url == reverse("accounts:password_reset_done")


@pytest.mark.django_db
def test_signed_in_user_is_sent_to_the_dashboard(client, make_user):
    make_user()
    client.login(username="ana@exemplo.com", password=PASSWORD)

    assert client.get(reverse(REQUEST)).status_code == 302
    assert client.get(reverse("accounts:password_reset_done")).status_code == 302


# --- new password ----------------------------------------------------------------------------


@pytest.mark.django_db
def test_valid_link_shows_the_form(client, make_user):
    make_user()
    ask_reset(client)

    response = open_link(client, reset_path())

    assert response.status_code == 200
    assert "Escolha uma nova senha" in response.content.decode()


@pytest.mark.django_db
def test_password_is_reset_and_user_goes_to_login(client, make_user):
    user = make_user()
    ask_reset(client)

    response = submit_new_password(client, reset_path())

    assert response.status_code == 302
    assert response.url == reverse("accounts:login")
    user.refresh_from_db()
    assert user.check_password(NEW_PASSWORD)
    assert user.password != NEW_PASSWORD
    assert SESSION_KEY not in client.session
    login = client.get(response.url).content.decode()
    assert "Senha redefinida. Entre com a nova senha." in login

    old = client.post(reverse("accounts:login"), {"username": user.email, "password": PASSWORD})
    new = client.post(reverse("accounts:login"), {"username": user.email, "password": NEW_PASSWORD})
    assert old.status_code == 200
    assert new.status_code == 302


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("password", "confirm", "expected"),
    [
        ("123", None, "muito curta"),
        ("12345678", None, "muito comum"),
        (NEW_PASSWORD, "diferente-123456", "não correspondem"),
    ],
)
def test_weak_password_or_mismatch_keeps_password_and_link(
    client, make_user, password, confirm, expected
):
    user = make_user()
    ask_reset(client)
    path = reset_path()

    response = submit_new_password(client, path, password, confirm)

    assert response.status_code == 200
    assert expected in response.content.decode()
    user.refresh_from_db()
    assert user.check_password(PASSWORD)
    assert open_link(Client(), path).status_code == 200
    assert "Escolha uma nova senha" in open_link(Client(), path).content.decode()


@pytest.mark.django_db
def test_used_link_shows_the_generic_message(client, make_user):
    make_user()
    ask_reset(client)
    path = reset_path()
    submit_new_password(client, path)

    response = open_link(Client(), path)

    assert INVALID_TITLE in response.content.decode()


@pytest.mark.django_db
def test_expired_link_shows_the_generic_message(client, make_user, settings):
    settings.PASSWORD_RESET_LINK_TIMEOUT = -1
    user = make_user()
    ask_reset(client)

    response = open_link(client, reset_path())

    assert INVALID_TITLE in response.content.decode()
    user.refresh_from_db()
    assert user.check_password(PASSWORD)


@pytest.mark.django_db
def test_tampered_links_show_the_same_message(client, make_user):
    make_user()
    ask_reset(client)
    good = reset_path()
    uid = good.split("/")[-3]
    pages = [
        open_link(client, f"/accounts/password-reset/{uid}/abc-123/").content,
        open_link(client, "/accounts/password-reset/xyz/abc-123/").content,
        open_link(client, "/accounts/password-reset/MTIzNDU2/abc-123/").content,
    ]

    for page in pages:
        assert INVALID_TITLE in page.decode()
    assert pages[0] == pages[1] == pages[2]


@pytest.mark.django_db
def test_confirmation_link_does_not_open_a_reset(client, make_user):
    make_user(confirmed=False)
    client.post(reverse("accounts:resend"), {"email": "ana@exemplo.com"})
    token_path = confirmation_path().replace("/confirm/", "/password-reset/")

    response = open_link(client, token_path)

    assert INVALID_TITLE in response.content.decode()


@pytest.mark.django_db
def test_open_session_elsewhere_is_ended_by_the_reset(make_user):
    make_user()
    other = Client()
    other.login(username="ana@exemplo.com", password=PASSWORD)
    assert other.get(reverse("home")).status_code == 200
    requester = Client()
    ask_reset(requester)

    submit_new_password(requester, reset_path())

    response = other.get(reverse("home"))
    assert response.status_code == 302
    assert reverse("accounts:login") in response.url


@pytest.mark.django_db
def test_reset_lifts_a_login_lock(client, make_user):
    make_user()
    for _ in range(5):
        client.post(reverse("accounts:login"), {"username": "ana@exemplo.com", "password": "x"})
    assert throttle.is_locked("ana@exemplo.com")
    ask_reset(client)

    submit_new_password(client, reset_path())

    assert not LoginThrottle.objects.exists()
    response = client.post(
        reverse("accounts:login"), {"username": "ana@exemplo.com", "password": NEW_PASSWORD}
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_flow_does_not_distinguish_registered_from_unregistered_email(make_user):
    make_user()
    outcomes = []
    for email in ("ana@exemplo.com", "ninguem@exemplo.com"):
        client = Client()
        request = ask_reset(client, email)
        done = client.get(request.url)
        outcomes.append((request.status_code, request.url, done.status_code, done.content))

    assert outcomes[0] == outcomes[1]
