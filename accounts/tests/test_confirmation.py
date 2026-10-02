from datetime import datetime, timedelta

import pytest
from django.core import mail
from django.urls import reverse

from accounts.emails import send_confirmation_email
from accounts.tokens import email_confirmation_token

from .conftest import confirmation_path


def pending_link(user):
    send_confirmation_email(user)
    return confirmation_path()


@pytest.mark.django_db
def test_valid_link_confirms_the_account(client, make_user):
    user = make_user(confirmed=False)

    response = client.get(pending_link(user))

    assert response.status_code == 200
    assert response.context["outcome"] == "confirmed"
    assert "Conta confirmada" in response.content.decode()
    user.refresh_from_db()
    assert user.is_email_confirmed


@pytest.mark.django_db
def test_link_is_single_use(client, make_user):
    user = make_user(confirmed=False)
    link = pending_link(user)

    client.get(link)
    second = client.get(link)

    assert second.context["outcome"] == "already"
    assert "já foi confirmado" in second.content.decode()


@pytest.mark.django_db
def test_expired_link_does_not_confirm(client, make_user, monkeypatch, settings):
    user = make_user(confirmed=False)
    link = pending_link(user)
    later = datetime.now() + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT + 60)
    monkeypatch.setattr(email_confirmation_token, "_now", lambda: later)

    response = client.get(link)

    assert response.context["outcome"] == "invalid"
    assert "inválido ou expirado" in response.content.decode()
    assert reverse("accounts:resend") in response.content.decode()
    user.refresh_from_db()
    assert not user.is_email_confirmed


@pytest.mark.django_db
def test_link_still_valid_just_before_expiry(client, make_user, monkeypatch, settings):
    user = make_user(confirmed=False)
    link = pending_link(user)
    later = datetime.now() + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT - 60)
    monkeypatch.setattr(email_confirmation_token, "_now", lambda: later)

    assert client.get(link).context["outcome"] == "confirmed"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path", ["/accounts/confirm/!!!/abc-123/", "/accounts/confirm/MTk5OQ/zzz-zzz/"]
)
def test_tampered_link_is_invalid(client, make_user, path):
    user = make_user(confirmed=False)

    response = client.get(path)

    assert response.context["outcome"] == "invalid"
    user.refresh_from_db()
    assert not user.is_email_confirmed


@pytest.mark.django_db
def test_wrong_token_for_real_user_is_invalid(client, make_user):
    user = make_user(confirmed=False)
    link = pending_link(user)
    broken = link[:-2] + ("a" if link[-2] != "a" else "b") + "/"

    response = client.get(broken)

    assert response.context["outcome"] == "invalid"
    user.refresh_from_db()
    assert not user.is_email_confirmed


@pytest.mark.django_db
def test_link_of_a_changed_email_is_void(client, make_user):
    user = make_user(confirmed=False)
    link = pending_link(user)
    user.email = "outro@exemplo.com"
    user.save()

    assert client.get(link).context["outcome"] == "invalid"


@pytest.mark.django_db
def test_resend_sends_only_to_pending_accounts(client, make_user):
    make_user("pendente@exemplo.com", confirmed=False)
    make_user("confirmada@exemplo.com", confirmed=True)
    make_user("desativada@exemplo.com", confirmed=False, is_active=False)

    responses = {}
    for email in (
        "PENDENTE@exemplo.com",
        "confirmada@exemplo.com",
        "desativada@exemplo.com",
        "ninguem@exemplo.com",
    ):
        responses[email] = client.post(reverse("accounts:resend"), {"email": email})

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["pendente@exemplo.com"]
    # Every answer is the same redirect, so nothing reveals which accounts exist.
    assert {r.status_code for r in responses.values()} == {302}
    assert {r.url for r in responses.values()} == {reverse("accounts:resend_done")}
    done = client.get(reverse("accounts:resend_done")).content.decode()
    assert "Se houver uma conta pendente" in done


@pytest.mark.django_db
def test_resend_swallows_send_failures(client, make_user, monkeypatch):
    make_user("pendente@exemplo.com", confirmed=False)

    def boom(user):
        raise OSError("down")

    monkeypatch.setattr("accounts.views.send_confirmation_email", boom)

    response = client.post(reverse("accounts:resend"), {"email": "pendente@exemplo.com"})

    assert response.status_code == 302


@pytest.mark.django_db
def test_resend_form_validates_and_prefills_email(client):
    page = client.get(reverse("accounts:resend") + "?email=ana@exemplo.com")
    assert 'value="ana@exemplo.com"' in page.content.decode()

    bad = client.post(reverse("accounts:resend"), {"email": "x"})
    assert bad.status_code == 200
    assert bad.context["form"].errors["email"]
