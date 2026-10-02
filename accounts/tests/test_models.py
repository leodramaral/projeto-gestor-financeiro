import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_create_user_normalizes_email_and_hashes_password():
    user = User.objects.create_user("Ana@Exemplo.COM", "senha-segura-123", name="Ana")

    assert user.email == "ana@exemplo.com"
    assert user.password != "senha-segura-123"
    assert user.check_password("senha-segura-123")
    assert not user.is_staff
    assert not user.is_superuser
    assert user.email_confirmed_at is None
    assert not user.is_email_confirmed


@pytest.mark.django_db
def test_create_user_requires_email():
    with pytest.raises(ValueError):
        User.objects.create_user("", "senha-segura-123", name="Ana")


@pytest.mark.django_db
def test_create_superuser_is_staff_and_confirmed():
    admin = User.objects.create_superuser("root@exemplo.com", "senha-segura-123", name="Root")

    assert admin.is_staff
    assert admin.is_superuser
    assert admin.is_email_confirmed


@pytest.mark.django_db
def test_create_superuser_rejects_non_staff():
    with pytest.raises(ValueError):
        User.objects.create_superuser("root@exemplo.com", "x", name="Root", is_staff=False)


@pytest.mark.django_db
def test_database_rejects_emails_differing_only_by_case():
    User.objects.create_user("ana@exemplo.com", "senha-segura-123", name="Ana")

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(email="ANA@exemplo.com", name="Outra")


def test_user_names_and_str():
    user = User(email="ana@exemplo.com", name="Ana Souza")

    assert str(user) == "ana@exemplo.com"
    assert user.get_full_name() == "Ana Souza"
    assert user.get_short_name() == "Ana"
    assert User(email="a@b.com", name="").get_short_name() == "a@b.com"


def test_clean_normalizes_email():
    user = User(email="  Ana@Exemplo.com ", name="Ana")
    user.clean()

    assert user.email == "ana@exemplo.com"


@pytest.mark.django_db
def test_admin_changelist_opens_for_superuser(client):
    admin = User.objects.create_superuser("root@exemplo.com", "senha-segura-123", name="Root")
    client.force_login(admin)

    response = client.get(reverse("admin:accounts_user_changelist"))

    assert response.status_code == 200
    assert "root@exemplo.com" in response.content.decode()
