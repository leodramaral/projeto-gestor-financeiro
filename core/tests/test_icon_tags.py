import pytest
from django.template import Context, Template

from core.templatetags.icon_tags import ICON_DIR, icon_names


def render(source):
    return Template("{% load icon_tags %}" + source).render(Context())


def test_the_tag_draws_the_icon_inline_with_the_given_classes():
    html = render('{% lucide "sparkle" "h-4 w-4 text-brand-500" %}')

    assert html.startswith('<svg class="h-4 w-4 text-brand-500" aria-hidden="true"')
    assert 'stroke="currentColor"' in html and html.endswith("</svg>")


def test_the_classes_are_escaped_even_when_they_come_from_a_variable():
    html = Template('{% load icon_tags %}{% lucide "plus" css %}').render(
        Context({"css": 'x" onload="alert(1)'})
    )

    assert 'onload="alert(1)"' not in html
    assert "&quot; onload=&quot;alert(1)" in html


def test_the_default_size_is_applied():
    assert 'class="h-5 w-5"' in render('{% lucide "circle-alert" %}')


@pytest.mark.parametrize("name", ["", "Plus", "a/b", "../../settings", "plus.svg", "nao-existe"])
def test_only_a_plain_name_of_an_existing_file_is_accepted(name):
    with pytest.raises(ValueError, match="Unknown Lucide icon"):
        Template("{% load icon_tags %}{% lucide name %}").render(Context({"name": name}))


@pytest.mark.parametrize("name", icon_names())
def test_every_icon_file_is_a_clean_lucide_svg(name):
    svg = (ICON_DIR / f"{name}.svg").read_text()

    assert svg.startswith("<svg ") and 'stroke="currentColor"' in svg
    assert "<script" not in svg and " width=" not in svg.split(">", 1)[0]


def test_the_assistant_icons_are_in_the_folder():
    assert {"message-square-more", "sparkle", "circle-alert"} <= set(icon_names())
