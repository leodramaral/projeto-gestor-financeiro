import re

import pytest
from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message
from django.template.loader import render_to_string

LEVELS = ["success", "error", "warning", "info"]


def templates_html():
    return render_to_string("partials/toast_templates.html")


def messages_html(*messages):
    return render_to_string("partials/toast_messages.html", {"messages": list(messages)})


def test_there_is_one_template_per_level_with_an_empty_text_slot_and_a_close_button():
    html = templates_html()

    for level in LEVELS:
        assert f'<template data-toast-level="{level}">' in html
    assert html.count("<template ") == 4
    assert html.count("data-toast-text") == 4 and html.count("data-toast-close") == 4
    assert re.search(r"data-toast-text[^>]*></p>", html)


@pytest.mark.parametrize("level", LEVELS)
def test_each_template_has_the_title_role_and_icon_of_its_level(level):
    html = templates_html()
    template = html.split(f'<template data-toast-level="{level}">')[1].split("</template>")[0]
    role = {"success": "status", "error": "alert", "warning": "alert", "info": "status"}[level]

    assert f'data-level="{level}"' in template and f'role="{role}"' in template


def test_each_message_becomes_a_hidden_data_element_with_its_level():
    html = messages_html(Message(constants.SUCCESS, "Lançamento registrado."))

    assert '<div hidden data-toast data-level="success">Lançamento registrado.</div>' in html


def test_several_messages_make_several_elements_in_order():
    html = messages_html(Message(constants.SUCCESS, "Um."), Message(constants.ERROR, "Dois."))

    assert html.count("data-toast data-level=") == 2
    assert html.index("Um.") < html.index("Dois.")
    assert 'data-level="error">Dois.</div>' in html


def test_an_unknown_level_is_an_info_toast():
    html = messages_html(Message(99, "Estranha."))

    assert '<div hidden data-toast data-level="info">Estranha.</div>' in html


def test_the_text_is_escaped():
    html = messages_html(Message(constants.INFO, "<script>alert(1)</script>"))

    assert "<script>" not in html and "&lt;script&gt;" in html


def test_each_message_also_comes_as_a_static_alert_inside_noscript():
    html = messages_html(Message(constants.SUCCESS, "Lançamento registrado."))
    fallback = html.split("<noscript>")[1].split("</noscript>")[0]

    assert 'role="status"' in fallback and ">Lançamento registrado.</p>" in fallback
    assert "data-toast-close" not in fallback


def test_without_messages_nothing_is_rendered():
    assert messages_html().strip() == ""
