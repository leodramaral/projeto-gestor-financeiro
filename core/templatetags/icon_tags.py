import re
from functools import cache
from pathlib import Path

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

ICON_DIR = Path(__file__).resolve().parent.parent / "icons"
NAME = re.compile(r"[a-z0-9-]+")


def icon_names():
    return sorted(path.stem for path in ICON_DIR.glob("*.svg"))


@cache
def _svg(name):
    return (ICON_DIR / f"{name}.svg").read_text().strip()


@register.simple_tag
def lucide(name, css="h-5 w-5"):
    """Inline Lucide SVG from `core/icons/`, drawn in `currentColor` and hidden from screen readers.

    The standard for the icons of the interface: add the file (with the Lucide name) to the folder
    instead of drawing a new SVG. Only a plain name of a file in the folder reaches the file system.
    """
    if not NAME.fullmatch(name) or not (ICON_DIR / f"{name}.svg").is_file():
        raise ValueError(f"Unknown Lucide icon: {name!r}; add it to core/icons/.")
    attrs = format_html('class="{}" aria-hidden="true" focusable="false"', css)
    # Safe: `name` is a plain name of a file in ICON_DIR (checked above), so the markup is our own;
    # `css` goes through format_html, which escapes it.
    return mark_safe(_svg(name).replace("<svg ", f"<svg {attrs} ", 1))  # noqa: S308
