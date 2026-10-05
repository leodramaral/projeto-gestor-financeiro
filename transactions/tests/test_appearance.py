import re
from pathlib import Path

import pytest
from django.conf import settings

from transactions.appearance import COLORS, ICONS

TEXT_CONTRAST = 4.5
FILL_CONTRAST = 3.0
LIGHT_SURFACE = "#ffffff"
DARK_SURFACE = "#101828"
ICON_DIR = Path(settings.BASE_DIR) / "transactions" / "icons"


def luminance(hex_color):
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_there_are_20_icons_and_8_colors_without_duplicates():
    assert len(ICONS) == 20
    assert len({i.key for i in ICONS}) == 20
    assert len({i.label for i in ICONS}) == 20
    assert len(COLORS) == 8
    assert len({c.key for c in COLORS}) == 8


def test_palette_has_no_red():
    assert "red" not in {c.key for c in COLORS}


@pytest.mark.parametrize("color", COLORS, ids=lambda c: c.key)
def test_badge_icon_is_readable_on_its_tint_in_both_modes(color):
    assert contrast(color.chip_text, color.chip_bg) >= TEXT_CONTRAST
    assert contrast(color.chip_text_dark, color.chip_bg_dark) >= TEXT_CONTRAST


@pytest.mark.parametrize("color", COLORS, ids=lambda c: c.key)
def test_fill_stands_out_from_the_surface_in_both_modes(color):
    assert contrast(color.fill, LIGHT_SURFACE) >= FILL_CONTRAST
    assert contrast(color.fill_dark, DARK_SURFACE) >= FILL_CONTRAST


def test_every_icon_has_its_svg_and_nothing_else_was_copied():
    files = {p.stem for p in ICON_DIR.glob("*.svg")}

    assert files == {i.key for i in ICONS}
    for icon in ICONS:
        svg = (ICON_DIR / f"{icon.key}.svg").read_text()
        assert svg.startswith("<svg ") and svg.rstrip().endswith("</svg>")
        assert 'stroke="currentColor"' in svg


def test_svgs_are_clean_and_carry_no_script():
    for path in ICON_DIR.glob("*.svg"):
        svg = path.read_text()
        root = svg[: svg.index(">") + 1]
        assert not re.search(r"\s(width|height|class)=", root)
        assert "<script" not in svg and "<style" not in svg


def test_the_icon_license_is_kept_next_to_the_files():
    assert "ISC License" in (ICON_DIR / "LICENSE").read_text()


def test_every_color_has_its_css_classes_with_the_same_values():
    css = (Path(settings.BASE_DIR) / "frontend" / "style.css").read_text()

    for color in COLORS:
        assert f".cat-{color.key} " in css
        assert f".dark .cat-{color.key} " in css
        for value in (color.fill, color.chip_bg, color.chip_text, color.chip_bg_dark):
            assert value in css
