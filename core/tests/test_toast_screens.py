import re

import pytest
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, Template
from django.urls import path, reverse

from config import urls as project_urls
from core.tests.toast_html import inline_alerts, noscript_fallback, toasts

PAGE = Template('{% extends "base.html" %}{% block content %}<p>Tela futura</p>{% endblock %}')


def future_add(request):
    messages.success(request, "Feito.")
    messages.error(request, "Falhou.")
    messages.warning(request, "Cuidado.")
    messages.info(request, "Veja <b>isto</b>.")
    messages.add_message(request, 99, "Nível estranho.")
    return redirect("future-page")


def future_page(request):
    return HttpResponse(PAGE.render(RequestContext(request)))


urlpatterns = [
    path("futuro/", future_page, name="future-page"),
    path("futuro/add/", future_add, name="future-add"),
    *project_urls.urlpatterns,
]

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def urlconf(settings):
    settings.ROOT_URLCONF = __name__


@pytest.fixture
def logged(client):
    user = get_user_model().objects.create_user("ana@exemplo.com", "senha-segura-123", name="Ana")
    client.force_login(user)
    return client


def test_a_new_screen_shows_the_messages_with_no_loop_of_its_own(logged):
    html = logged.get(reverse("future-add"), follow=True).content.decode()

    assert [level for level, _ in toasts(html)] == ["success", "error", "warning", "info", "info"]
    assert [text for _, text in toasts(html)][:3] == ["Feito.", "Falhou.", "Cuidado."]
    assert inline_alerts(html) == 0


def test_the_text_of_a_message_is_escaped_and_an_unknown_level_is_info(logged):
    html = logged.get(reverse("future-add"), follow=True).content.decode()

    assert ("info", "Veja &lt;b&gt;isto&lt;/b&gt;.") in toasts(html)
    assert "<b>isto</b>" not in html
    assert ("info", "Nível estranho.") in toasts(html)


def test_each_message_also_has_its_static_alert_for_when_javascript_is_off(logged):
    html = logged.get(reverse("future-add"), follow=True).content.decode()

    assert noscript_fallback(html).count('role="alert"') == 2  # error and warning
    assert 'data-level="success"' in noscript_fallback(html)


def test_a_page_without_messages_has_no_toast_and_no_alert(logged):
    html = logged.get(reverse("future-page")).content.decode()

    assert toasts(html) == [] and inline_alerts(html) == 0
    assert 'x-data="toastStack"' in html and html.count("<template data-toast-level=") == 4


def assert_loads_toast_and_nothing_external(html):
    assert 'x-data="toastStack"' in html
    assert html.index("js/toast.js") < html.index("alpine.min.js")
    assert re.findall(r'(?:src|href)="(https?://[^"]+)"', html) == []


def test_the_panel_layout_loads_the_toast_script_before_alpine_and_nothing_from_outside(logged):
    assert_loads_toast_and_nothing_external(logged.get(reverse("future-page")).content.decode())


@pytest.mark.parametrize("url", ["accounts:login", "accounts:signup"])
def test_the_guest_layouts_load_the_toast_script_before_alpine_and_nothing_from_outside(
    client, url
):
    assert_loads_toast_and_nothing_external(client.get(reverse(url)).content.decode())
