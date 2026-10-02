import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.fixture
def logged_client(client):
    user = get_user_model().objects.create_user("ana@exemplo.com", "senha-segura-123", name="Ana")
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_home_renders_base_layout(logged_client):
    """The dashboard renders the base layout with its sidebar and header partials."""
    response = logged_client.get(reverse("home"))

    assert response.status_code == 200
    templates = [t.name for t in response.templates]
    assert "base.html" in templates
    assert "partials/sidebar.html" in templates
    assert "partials/header.html" in templates
    content = response.content.decode()
    assert "Olá, mundo" in content
    assert "<main>" in content


def test_pytest_uses_test_settings():
    """Pytest runs with the test settings module, not dev or prod."""
    assert settings.SETTINGS_MODULE == "config.settings.test"
