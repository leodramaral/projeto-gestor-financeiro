from functools import cache
from pathlib import Path

from django import template
from django.utils.safestring import mark_safe

from transactions.appearance import COLOR_BY_KEY, DEFAULT_COLOR, DEFAULT_ICON, ICON_BY_KEY

register = template.Library()

ICON_DIR = Path(__file__).resolve().parent.parent / "icons"


@cache
def _svg(key):
    return (ICON_DIR / f"{key}.svg").read_text().strip()


@register.simple_tag
def category_icon(key, css="h-5 w-5"):
    """Inline Lucide SVG for a listed icon key ("" for anything else), drawn in `currentColor`.

    Only keys from the fixed list reach the file system, so nothing a user typed becomes a path.
    """
    if key not in ICON_BY_KEY:
        return ""
    attrs = f'class="cat-icon {css}" aria-hidden="true" focusable="false"'
    # Safe: `key` is in ICON_BY_KEY (checked above), so the markup comes from our own SVG files.
    return mark_safe(_svg(key).replace("<svg ", f"<svg {attrs} ", 1))  # noqa: S308


def _color_key(category):
    return category.color if category.color in COLOR_BY_KEY else DEFAULT_COLOR


def _icon_key(category):
    return category.icon if category.icon in ICON_BY_KEY else DEFAULT_ICON


@register.inclusion_tag("partials/category_chip.html")
def category_chip(category):
    """Pill with the category's icon and name, tinted with its color."""
    return {"name": category.name, "icon": _icon_key(category), "color": _color_key(category)}


@register.inclusion_tag("partials/category_badge.html")
def category_badge(category, size="md"):
    """Rounded square with the category's icon over its color tint."""
    return {"icon": _icon_key(category), "color": _color_key(category), "size": size}


@register.inclusion_tag("partials/category_select.html")
def category_select(name, field_id, categories, selected, placeholder, label, css=""):
    """Floating select for categories; a plain `<select>` underneath keeps it working without JS."""
    selected = str(selected) if selected not in (None, "") else ""
    options = [
        {
            "pk": str(category.pk),
            "name": category.name,
            "icon": _icon_key(category),
            "color": _color_key(category),
        }
        for category in categories
    ]
    return {
        "name": name,
        "field_id": field_id,
        "options": options,
        "selected": selected,
        "placeholder": placeholder,
        "label": label,
        "css": css,
    }
