import xml.etree.ElementTree as ET

import pytest
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import Client
from django.urls import reverse

VISITOR_PAGES = [
    reverse("accounts:login"),
    reverse("accounts:signup"),
    reverse("accounts:signup_done"),
    reverse("accounts:resend"),
    reverse("accounts:resend_done"),
    reverse("accounts:password_reset"),
    reverse("accounts:password_reset_done"),
    "/accounts/confirm/MQ/token-invalido/",
]
EMAIL_CONTEXT = {
    "name": "Ana",
    "confirm_url": "http://testserver/x/",
    "reset_url": "http://testserver/x/",
    "site_url": "http://testserver",
    "valid_days": 3,
}
EMAILS = ["confirm_account", "password_reset", "test_message"]


@pytest.fixture
def logged_client(client):
    user = get_user_model().objects.create_user("ana@exemplo.com", "senha-segura-123", name="Ana")
    client.force_login(user)
    return client


def test_new_brand_assets_exist_and_old_ones_are_gone():
    assert finders.find("images/logo/logo-icon.svg")
    assert finders.find("images/favicon.svg")
    for old in ("images/logo/logo.svg", "images/logo/logo-dark.svg", "images/favicon.ico"):
        assert not finders.find(old), old


@pytest.mark.parametrize("asset", ["images/logo/logo-icon.svg", "images/favicon.svg"])
def test_brand_svg_is_valid_and_uses_the_brand_color(asset):
    root = ET.parse(finders.find(asset)).getroot()

    assert root.tag.endswith("svg")
    assert root.attrib["viewBox"] == "0 0 48 48"
    assert "#0F766E" in ET.tostring(root, encoding="unicode")


@pytest.mark.django_db
def test_dashboard_shows_the_brand_in_sidebar_and_mobile_header(logged_client):
    response = logged_client.get(reverse("transactions:list"))

    content = response.content.decode()
    assert "partials/brand.html" in [t.name for t in response.templates]
    # Sidebar: full brand (icon + name) and the icon-only version for the collapsed bar.
    assert content.count('aria-label="Gestor Financeiro"') >= 4
    assert content.count(">Gestor Financeiro</span>") >= 2
    assert 'class="logo-icon"' in content


@pytest.mark.django_db
@pytest.mark.parametrize("url", VISITOR_PAGES[:2])
def test_visitor_pages_show_the_brand(client, url):
    response = client.get(url)

    assert "partials/brand.html" in [t.name for t in response.templates]
    assert ">Gestor Financeiro</span>" in response.content.decode()


@pytest.mark.django_db
def test_favicon_is_the_brand_svg_on_every_layout(logged_client):
    visitor = Client().get(reverse("accounts:login"))
    for page in (visitor, logged_client.get(reverse("transactions:list"))):
        content = page.content.decode()
        assert 'rel="icon" type="image/svg+xml"' in content
        assert "images/favicon.svg" in content
        assert "favicon.ico" not in content


@pytest.mark.django_db
@pytest.mark.parametrize("url", VISITOR_PAGES)
def test_no_tailadmin_text_on_visitor_pages(client, url):
    assert "tailadmin" not in client.get(url).content.decode().lower()


@pytest.mark.django_db
def test_no_tailadmin_text_on_the_dashboard(logged_client):
    assert (
        "tailadmin" not in logged_client.get(reverse("transactions:list")).content.decode().lower()
    )


@pytest.mark.parametrize("name", EMAILS)
@pytest.mark.parametrize("ext", ["html", "txt"])
def test_no_tailadmin_text_in_emails(name, ext):
    rendered = render_to_string(f"email/{name}.{ext}", EMAIL_CONTEXT)

    assert "tailadmin" not in rendered.lower()


THEME_TOGGLE = 'aria-label="Alternar tema"'


@pytest.mark.django_db
def test_dashboard_keeps_the_theme_toggle_in_the_header(logged_client):
    response = logged_client.get(reverse("transactions:list"))

    assert "partials/theme_toggle.html" in [t.name for t in response.templates]
    assert THEME_TOGGLE in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize("url", VISITOR_PAGES)
def test_visitor_pages_offer_the_theme_toggle(client, url):
    content = client.get(url).content.decode()

    assert THEME_TOGGLE in content
    assert 'x-data="{ darkMode:' in content
    assert "setTheme(darkMode)" in content


@pytest.mark.django_db
def test_both_layouts_apply_the_saved_theme_before_the_stylesheet(logged_client):
    pages = [
        Client().get(reverse("accounts:login")),
        logged_client.get(reverse("transactions:list")),
    ]
    for response in pages:
        assert "partials/theme_init.html" in [t.name for t in response.templates]
        content = response.content.decode()
        assert content.index("window.setTheme") < content.index("dist/css/style.css")


def test_theme_init_tolerates_blocked_storage():
    script = render_to_string("partials/theme_init.html")

    # Both the read and the write of the saved theme are guarded, so a blocked
    # localStorage leaves the page working in the light theme.
    assert script.count("try {") == 2
    assert script.count("catch (e)") == 2
