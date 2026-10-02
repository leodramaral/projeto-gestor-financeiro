import re
from pathlib import Path

import pytest
from django.conf import settings

STYLE_CSS = Path(settings.BASE_DIR) / "frontend" / "style.css"
OLD_BLUE = "#465fff"
MIN_CONTRAST = 4.5
SCALE = ["25", "50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950"]


def token(name):
    match = re.search(rf"--color-{name}:\s*(#[0-9a-fA-F]{{6}})\s*;", STYLE_CSS.read_text())
    assert match, f"token --color-{name} not found in frontend/style.css"
    return match.group(1).lower()


def luminance(hex_color):
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    lighter, darker = sorted((luminance(a), luminance(b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def test_brand_scale_is_complete_and_no_longer_the_template_blue():
    for step in SCALE:
        assert token(f"brand-{step}") != OLD_BLUE
    assert token("brand-500") == "#0f766e"


def test_brand_scale_gets_darker_step_by_step():
    lums = [luminance(token(f"brand-{step}")) for step in SCALE]

    assert lums == sorted(lums, reverse=True)


@pytest.mark.parametrize(
    ("label", "foreground", "background"),
    [
        ("white text on the primary button", "#ffffff", "brand-500"),
        ("white text on the button hover", "#ffffff", "brand-600"),
        ("brand link text on white", "brand-600", "#ffffff"),
        ("brand text on the dark page background", "brand-400", "gray-900"),
        ("icon glyph on the dark icon background", "brand-700", "brand-300"),
    ],
)
def test_brand_color_pairs_meet_wcag_aa(label, foreground, background):
    def resolve(value):
        return value if value.startswith("#") else token(value)

    ratio = contrast(resolve(foreground), resolve(background))

    assert ratio >= MIN_CONTRAST, f"{label}: {ratio:.2f}:1"


def test_no_template_or_stylesheet_uses_the_old_blue():
    templates = [p for p in (Path(settings.BASE_DIR) / "templates").rglob("*") if p.is_file()]
    offenders = [str(f) for f in [*templates, STYLE_CSS] if OLD_BLUE in f.read_text().lower()]

    assert offenders == []


def test_brand_text_in_templates_has_a_lighter_tone_for_the_dark_theme():
    """`brand-500` is dark: as text on a dark background it needs `dark:text-brand-400`."""
    class_lists = [
        (path.name, attrs.split())
        for path in (Path(settings.BASE_DIR) / "templates").rglob("*.html")
        for attrs in re.findall(r'class="([^"]*)"', path.read_text())
    ]
    offenders = [
        (name, classes)
        for name, classes in class_lists
        if "text-brand-500" in classes and "dark:text-brand-400" not in classes
    ]

    assert offenders == []
