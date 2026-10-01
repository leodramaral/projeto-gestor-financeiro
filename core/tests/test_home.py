from django.conf import settings
from django.urls import reverse


def test_home_renders_base_layout(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    templates = [t.name for t in response.templates]
    assert "base.html" in templates
    assert "partials/sidebar.html" in templates
    assert "partials/header.html" in templates
    content = response.content.decode()
    assert "Olá, mundo" in content
    assert "<main>" in content


def test_pytest_uses_test_settings():
    assert settings.SETTINGS_MODULE == "config.settings.test"
