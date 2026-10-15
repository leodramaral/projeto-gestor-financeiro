import pytest
from django.test import Client
from django.urls import reverse

from assistant import views

CHAT = "/assistant/"
NEW = "/assistant/new/"


@pytest.fixture(autouse=True)
def provider_is_off_limits(monkeypatch):
    """Nobody in this module may reach the provider."""

    monkeypatch.setattr(
        views, "answer", lambda *args, **kwargs: pytest.fail("The provider must not be called.")
    )


def test_the_routes_are_where_the_spec_says():
    assert reverse("assistant:chat") == CHAT
    assert reverse("assistant:new") == NEW


@pytest.mark.parametrize("method", ["get", "post"])
def test_a_visitor_is_sent_to_the_login(client, method):
    response = getattr(client, method)(CHAT, {"question": "oi"})

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


def test_a_visitor_cannot_start_a_new_conversation(client):
    response = client.post(NEW)

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


def test_getting_the_page_does_not_ask_the_provider(logged):
    assert logged.get(CHAT).status_code == 200


def test_the_new_conversation_route_only_accepts_post(logged):
    assert logged.get(NEW).status_code == 405


def test_the_page_shows_the_field_notice_and_credits(logged):
    html = logged.get(CHAT).content.decode()

    assert "<title>Assistente · Gestor Financeiro</title>" in html
    assert "Sua pergunta" in html
    assert "sugestões automatizadas" in html
    assert "Créditos de hoje" in html
    assert "40.000" in html


def test_the_sidebar_item_is_active_on_the_page_and_not_elsewhere(logged):
    link = f'href="{CHAT}"'

    on_page = logged.get(CHAT).content.decode()
    elsewhere = logged.get("/").content.decode()

    assert link in elsewhere
    assert 'aria-current="page"' in on_page.split(link, 1)[1].split("</a>", 1)[0]
    assert 'aria-current="page"' not in elsewhere.split(link, 1)[1].split("</a>", 1)[0]


def test_the_empty_conversation_invites_a_full_question(logged):
    html = logged.get(CHAT).content.decode()

    assert "Quanto gastei com transporte em agosto?" in html
    assert "Nova conversa" not in html


def test_a_page_without_the_key_says_the_assistant_is_unavailable(logged, settings):
    settings.LLM_API_KEY = ""

    html = logged.get(CHAT).content.decode()

    assert "O assistente está indisponível no momento." in html


def test_the_field_and_the_send_button_have_accessible_names(logged):
    html = logged.get(CHAT).content.decode()

    assert '<label for="id_question" class="sr-only">Sua pergunta</label>' in html
    assert 'aria-label="Enviar"' in html
    assert 'role="progressbar" aria-label="Créditos de hoje usados"' in html


def test_the_new_conversation_button_only_shows_with_a_conversation(logged):
    assert "Nova conversa" not in logged.get(CHAT).content.decode()

    session = logged.session
    session["assistant_conversation"] = [
        {"role": "user", "content": "pergunta"},
        {"role": "assistant", "content": "resposta"},
    ]
    session.save()
    html = logged.get(CHAT).content.decode()

    assert "Nova conversa" in html
    assert 'action="/assistant/new/"' in html


def test_the_messages_are_identified_for_screen_readers(logged):
    session = logged.session
    session["assistant_conversation"] = [
        {"role": "user", "content": "pergunta"},
        {"role": "assistant", "content": "resposta"},
    ]
    session.save()

    html = logged.get(CHAT).content.decode()

    assert '<span class="sr-only">Você: </span>pergunta' in html
    assert html.index("pergunta") < html.index("resposta")
    assert ">Assistente</span>" in html


def test_the_empty_page_shows_no_conversation_list(logged):
    assert "<ol" not in logged.get(CHAT).content.decode()


def test_the_sidebar_item_carries_the_beta_tag(logged):
    for url in (CHAT, "/"):
        html = logged.get(url).content.decode()
        item = html.split('href="/assistant/"', 1)[1].split("</a>", 1)[0]

        assert ">BETA</span>" in item
        assert "menu-item-badge" in item


def test_the_notice_in_the_body_says_the_assistant_is_in_beta(logged):
    html = logged.get(CHAT).content.decode()

    assert "Assistente em fase BETA: as respostas são sugestões automatizadas" in html


@pytest.mark.parametrize("route", [CHAT, NEW])
def test_a_post_without_the_csrf_token_is_refused(user, route):
    strict = Client(enforce_csrf_checks=True)
    strict.force_login(user)

    assert strict.post(route, {"question": "q"}).status_code == 403
