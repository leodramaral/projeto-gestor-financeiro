from datetime import timedelta

import pytest
from django.contrib.auth import SESSION_KEY
from django.urls import reverse
from django.utils import timezone

from accounts import throttle
from accounts.models import LoginThrottle

from .conftest import PASSWORD

LOGIN = "accounts:login"
LIMIT = 5  # LOGIN_MAX_FAILED_ATTEMPTS default


def fail(email="ana@exemplo.com", times=LIMIT):
    for _ in range(times):
        throttle.register_failure(email)


@pytest.mark.django_db
def test_locks_after_the_limit_and_not_before():
    fail(times=LIMIT - 1)
    assert not throttle.is_locked("ana@exemplo.com")

    throttle.register_failure("ana@exemplo.com")

    assert throttle.is_locked("ana@exemplo.com")


@pytest.mark.django_db
def test_email_case_shares_one_count():
    for email in ("Ana@Exemplo.com", " ANA@exemplo.com", "ana@exemplo.com"):
        fail(email, times=2)

    assert LoginThrottle.objects.count() == 1
    assert throttle.is_locked("ana@exemplo.com")


@pytest.mark.django_db
def test_lock_is_isolated_per_email():
    fail("ana@exemplo.com")

    assert not throttle.is_locked("bia@exemplo.com")


@pytest.mark.django_db
def test_lock_ends_with_time_and_next_failure_starts_a_fresh_count():
    fail()
    LoginThrottle.objects.update(locked_until=timezone.now() - timedelta(seconds=1))
    assert not throttle.is_locked("ana@exemplo.com")

    throttle.register_failure("ana@exemplo.com")

    row = LoginThrottle.objects.get()
    assert row.failed_count == 1
    assert row.locked_until is None


@pytest.mark.django_db
def test_reset_lifts_the_lock():
    fail()

    throttle.reset("ANA@exemplo.com")

    assert not throttle.is_locked("ana@exemplo.com")
    assert not LoginThrottle.objects.exists()


def post_login(client, email="ana@exemplo.com", password="errada"):
    return client.post(reverse(LOGIN), {"username": email, "password": password})


@pytest.mark.django_db
def test_login_locks_even_with_the_right_password(client, make_user):
    make_user()
    for _ in range(LIMIT):
        post_login(client)

    response = post_login(client, password=PASSWORD)

    assert response.status_code == 200
    assert SESSION_KEY not in client.session
    content = response.content.decode()
    assert "Muitas tentativas de login" in content
    assert "15 minutos" in content


@pytest.mark.django_db
def test_login_below_the_limit_works_and_resets_the_count(client, make_user):
    make_user()
    for _ in range(LIMIT - 1):
        post_login(client)

    post_login(client, password=PASSWORD)

    assert SESSION_KEY in client.session
    assert not LoginThrottle.objects.exists()


@pytest.mark.django_db
def test_unknown_email_hits_the_same_limit_and_message(client, make_user):
    make_user()
    for email in ("ana@exemplo.com", "ninguem@exemplo.com"):
        for _ in range(LIMIT):
            post_login(client, email)

    known = post_login(client, "ana@exemplo.com")
    unknown = post_login(client, "ninguem@exemplo.com")

    assert known.context["form"].non_field_errors() == unknown.context["form"].non_field_errors()
    assert "Muitas tentativas" in unknown.content.decode()


@pytest.mark.django_db
def test_lock_message_uses_the_remaining_time(client, make_user):
    make_user()
    for _ in range(LIMIT):
        post_login(client)
    LoginThrottle.objects.update(locked_until=timezone.now() + timedelta(seconds=30))

    response = post_login(client)

    assert "em 1 minuto." in response.content.decode()


@pytest.mark.django_db
def test_other_email_is_not_blocked(client, make_user):
    make_user("ana@exemplo.com")
    make_user("bia@exemplo.com")
    for _ in range(LIMIT):
        post_login(client)

    post_login(client, "bia@exemplo.com", PASSWORD)

    assert SESSION_KEY in client.session


@pytest.mark.django_db
def test_unconfirmed_account_does_not_count_as_a_failure(client, make_user):
    make_user(confirmed=False)

    for _ in range(LIMIT + 1):
        post_login(client, password=PASSWORD)

    assert not throttle.is_locked("ana@exemplo.com")


@pytest.mark.django_db
def test_lock_expires_and_login_works_again(client, make_user):
    make_user()
    for _ in range(LIMIT):
        post_login(client)
    LoginThrottle.objects.update(locked_until=timezone.now() - timedelta(seconds=1))

    post_login(client, password=PASSWORD)

    assert SESSION_KEY in client.session


@pytest.mark.django_db
def test_failure_during_an_active_lock_does_not_extend_it():
    fail()
    locked_until = LoginThrottle.objects.get().locked_until

    throttle.register_failure("ana@exemplo.com")

    row = LoginThrottle.objects.get()
    assert row.locked_until == locked_until
    assert row.failed_count == 0
