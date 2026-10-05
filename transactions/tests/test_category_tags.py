import pytest
from django.template import Context, Template

from transactions.appearance import ICONS
from transactions.models import Category


def render(source, **context):
    return Template("{% load category_tags %}" + source).render(Context(context))


@pytest.mark.parametrize("icon", ICONS, ids=lambda i: i.key)
def test_every_listed_icon_renders_an_inline_decorative_svg(icon):
    html = render("{% category_icon key %}", key=icon.key)

    assert html.startswith("<svg ")
    assert 'aria-hidden="true"' in html and 'focusable="false"' in html
    assert 'stroke="currentColor"' in html


@pytest.mark.parametrize("key", ["rocket", "../models", "", None, "🍔", "<script>"])
def test_unlisted_key_renders_nothing_and_never_reaches_the_file_system(key):
    assert render("{% category_icon key %}", key=key) == ""


def test_icon_takes_the_requested_size_classes():
    html = render('{% category_icon "car" "h-4 w-4" %}')

    assert 'class="cat-icon h-4 w-4"' in html


def test_chip_shows_icon_name_and_color_class():
    html = render("{% category_chip c %}", c=Category(name="Pets", icon="paw-print", color="amber"))

    assert "cat-amber" in html
    assert "Pets" in html
    assert "<svg" in html


def test_badge_shows_the_icon_in_two_sizes():
    category = Category(name="Pets", icon="paw-print", color="amber")

    medium = render("{% category_badge c %}", c=category)
    small = render('{% category_badge c "sm" %}', c=category)

    assert "h-10 w-10" in medium and "h-8 w-8" in small
    assert "cat-amber" in medium and "<svg" in small


def test_chip_and_badge_survive_an_unknown_icon_and_color():
    category = Category(name="Velha", icon="🦄", color="red")

    chip = render("{% category_chip c %}", c=category)
    badge = render("{% category_badge c %}", c=category)

    assert "Velha" in chip
    assert "cat-graphite" in chip and "cat-graphite" in badge
    assert "<svg" in chip and "<svg" in badge  # falls back to the default icon


def test_chip_escapes_the_category_name():
    html = render("{% category_chip c %}", c=Category(name="<b>x</b>", icon="gift", color="amber"))

    assert "<b>x</b>" not in html
    assert "&lt;b&gt;" in html
