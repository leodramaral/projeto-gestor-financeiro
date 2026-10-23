import pytest
from django.template.loader import render_to_string

# A fragment of each Lucide icon's drawing, enough to tell them apart in the rendered SVG.
ICON_MARK = {
    "success": "m16 9-5.5 5.5",
    "error": 'y1="8"',
    "warning": "m21.73 18",
    "info": "M12 16v-4",
}
TITLE = {
    "success": "Tudo certo",
    "error": "Algo deu errado",
    "warning": "Atenção",
    "info": "Informação",
}
ROLE = {"success": "status", "error": "alert", "warning": "alert", "info": "status"}
COLOR = {"success": "success", "error": "error", "warning": "warning", "info": "blue-light"}


def alert(**context):
    return render_to_string("partials/alert.html", {"message": "Texto.", **context})


@pytest.mark.parametrize("level", ["success", "error", "warning", "info"])
def test_each_level_has_its_own_icon_color_role_and_title(level):
    html = alert(level=level)

    assert ICON_MARK[level] in html
    assert f"border-{COLOR[level]}-500" in html
    assert f'role="{ROLE[level]}"' in html
    assert f'data-level="{level}"' in html
    assert f">{TITLE[level]}</h4>" in html
    assert ">Texto.</p>" in html


def test_without_a_level_the_alert_is_a_success_one():
    html = alert()

    assert 'data-level="success"' in html and ">Tudo certo</h4>" in html


def test_an_unknown_level_is_shown_as_info():
    html = alert(level="critical")

    assert 'data-level="info"' in html and ICON_MARK["info"] in html


def test_the_title_can_be_given():
    assert ">Pronto</h4>" in alert(level="error", title="Pronto")


def test_the_message_is_escaped():
    html = alert(message="<b>x</b>")

    assert "&lt;b&gt;x&lt;/b&gt;" in html and "<b>x</b>" not in html


def test_there_is_no_close_button_by_default():
    assert "data-toast-close" not in alert()


def test_a_closable_alert_gets_a_close_button_in_portuguese_with_the_lucide_x():
    html = alert(closable=True)

    assert "data-toast-close" in html
    assert 'aria-label="Fechar"' in html
    assert 'd="M18 6 6 18"' in html


@pytest.mark.parametrize("level", ["success", "error", "warning", "info"])
def test_the_dark_theme_gets_an_opaque_tinted_card(level):
    # Opaque (a color-mix of two opaque colors): the cards of a stack must not show through.
    color = COLOR[level]
    # Built in pieces on purpose: Tailwind scans the tests too and would take a half-filled class.
    tint = "dark:bg-[color-mix(in_srgb,var(--color-" + color + "-500)_15%,var(--color-gray-900))]"

    assert tint in alert(level=level)
