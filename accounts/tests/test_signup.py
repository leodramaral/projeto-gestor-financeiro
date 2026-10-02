from smtplib import SMTPException

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from .conftest import PASSWORD

User = get_user_model()
URL = "accounts:signup"
VALID = {
    "name": "Ana Souza",
    "email": "Ana@Exemplo.com",
    "password1": PASSWORD,
    "password2": PASSWORD,
}


@pytest.mark.django_db
def test_signup_page_renders(client):
    response = client.get(reverse(URL))

    assert response.status_code == 200
    assert "base_auth.html" in [t.name for t in response.templates]
    assert "partials/sidebar.html" not in [t.name for t in response.templates]


@pytest.mark.django_db
def test_signup_starts_focused_on_name_not_email(client):
    form = client.get(reverse(URL)).context["form"]

    assert form.fields["name"].widget.attrs.get("autofocus")
    assert "autofocus" not in form.fields["email"].widget.attrs
    assert "autofocus" not in form.fields["password1"].widget.attrs


@pytest.mark.django_db
def test_signup_shows_live_password_checklist_instead_of_static_list(client):
    content = client.get(reverse(URL)).content.decode()

    assert "Pelo menos 8 caracteres" in content
    assert "Não pode ser só números" in content
    assert "As senhas coincidem" in content
    # Only rules the browser can check live belong in the checklist.
    assert "Evite senhas comuns" not in content
    assert "alpine.min.js" in content
    # Django's own static help list must be gone.
    assert "Sua senha não pode ser muito parecida" not in content
    assert 'x-model="password1"' in content
    assert 'x-model="password2"' in content


@pytest.mark.django_db
def test_valid_signup_creates_unconfirmed_user_and_sends_link(client):
    response = client.post(reverse(URL), VALID)

    assert response.status_code == 302
    assert response.url == reverse("accounts:signup_done")
    user = User.objects.get()
    assert user.email == "ana@exemplo.com"
    assert user.email_confirmed_at is None
    assert user.password != PASSWORD
    assert "_auth_user_id" not in client.session
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["ana@exemplo.com"]
    assert "http://testserver/accounts/confirm/" in mail.outbox[0].body
    assert "Olá, Ana!" in mail.outbox[0].body
    assert client.get(response.url).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("password", ["curta1", "12345678901", "password123"])
def test_weak_password_is_rejected_in_portuguese(client, password):
    response = client.post(reverse(URL), {**VALID, "password1": password, "password2": password})

    assert response.status_code == 200
    assert not User.objects.exists()
    assert response.context["form"].errors["password2"]
    assert mail.outbox == []
    assert "Esta senha" in response.content.decode()


@pytest.mark.django_db
def test_password_similar_to_email_is_rejected(client):
    data = {
        **VALID,
        "email": "joaquimalberto@exemplo.com",
        "password1": "joaquimalberto",
        "password2": "joaquimalberto",
    }
    response = client.post(reverse(URL), data)

    assert not User.objects.exists()
    assert response.context["form"].errors["password2"]


@pytest.mark.django_db
def test_password_mismatch_is_rejected(client):
    response = client.post(reverse(URL), {**VALID, "password2": "outra-senha-123"})

    assert not User.objects.exists()
    assert response.context["form"].errors["password2"]


@pytest.mark.django_db
def test_invalid_email_is_rejected(client):
    response = client.post(reverse(URL), {**VALID, "email": "não-é-email"})

    assert response.status_code == 200
    assert not User.objects.exists()
    assert "email" in response.context["form"].errors


@pytest.mark.django_db
def test_name_is_required(client):
    response = client.post(reverse(URL), {**VALID, "name": ""})

    assert not User.objects.exists()
    assert "name" in response.context["form"].errors


@pytest.mark.django_db
def test_duplicate_email_with_other_case_shows_error_and_sends_nothing(client, make_user):
    make_user("ana@exemplo.com")

    response = client.post(reverse(URL), {**VALID, "email": "ANA@exemplo.com"})

    assert response.status_code == 200
    assert User.objects.count() == 1
    assert "Este e-mail já está cadastrado." in response.context["form"].errors["email"]
    assert "Este e-mail já está cadastrado." in response.content.decode()
    assert mail.outbox == []


@pytest.mark.django_db
def test_send_failure_rolls_back_the_user(client, monkeypatch):
    def boom(*args, **kwargs):
        raise SMTPException("down")

    monkeypatch.setattr("accounts.views.send_confirmation_email", boom)

    response = client.post(reverse(URL), VALID)

    assert response.status_code == 200
    assert not User.objects.exists()
    assert "Não foi possível enviar" in response.content.decode()


@pytest.mark.django_db
def test_signed_in_user_is_sent_to_dashboard(client, make_user):
    client.force_login(make_user())

    for name in (URL, "accounts:signup_done"):
        response = client.get(reverse(name))
        assert response.status_code == 302
        assert response.url == reverse("home")
