import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.fixture
def logged_client(client):
    user = get_user_model().objects.create_user("ana@exemplo.com", "senha-segura-123", name="Ana")
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_base_layout_restores_the_saved_sidebar_state(logged_client):
    content = logged_client.get(reverse("transactions:list")).content.decode()

    assert "partials/sidebar_init.html" in [
        t.name for t in logged_client.get(reverse("transactions:list")).templates
    ]
    assert "sidebarToggle: sidebarSaved()" in content
    assert "$watch('sidebarToggle'" in content
    assert "saveSidebar(collapsed)" in content


@pytest.mark.django_db
def test_collapsed_class_is_set_before_paint_and_handed_to_alpine(logged_client):
    content = logged_client.get(reverse("transactions:list")).content.decode()

    head = content.split("</head>")[0]
    assert 'classList.add("sidebar-collapsed")' in head
    assert "sidebar-ready" in content.split("<body")[1]
    assert "$nextTick" in content


def test_stylesheet_draws_the_collapsed_sidebar_without_waiting_for_alpine():
    from pathlib import Path

    from django.conf import settings

    css = (Path(settings.BASE_DIR) / "frontend" / "style.css").read_text()

    assert "html.sidebar-collapsed:not(.sidebar-ready) .sidebar" in css
    assert "width: 5.625rem" in css  # = Tailwind w-22.5, what Alpine applies when collapsed


@pytest.mark.django_db
def test_saved_state_is_only_kept_on_desktop_widths(logged_client):
    content = logged_client.get(reverse("transactions:list")).content.decode()

    assert 'var KEY = "sidebarCollapsed"' in content
    assert "var DESKTOP = 1280" in content
    # Both helpers bail out below the desktop breakpoint (mobile "open" means the drawer).
    assert content.count("window.innerWidth") >= 2


@pytest.mark.django_db
def test_storage_failures_are_swallowed(logged_client):
    content = logged_client.get(reverse("transactions:list")).content.decode()

    script = content.split("var KEY")[1].split("</script>")[0]
    assert script.count("catch (e)") == 2


def test_guest_layout_does_not_load_the_sidebar_state(client):
    assert "sidebarSaved" not in client.get(reverse("accounts:login")).content.decode()
