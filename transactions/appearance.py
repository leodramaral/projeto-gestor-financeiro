"""Fixed icon and color lists for categories.

The database stores the Lucide icon key and the color key; the SVG files (`transactions/icons/`) and
the CSS only come in when drawing, so changing either needs no migration. Hex values mirror the
`.cat-<key>` classes in `frontend/style.css` (a test keeps them in step).
"""

from dataclasses import dataclass

DEFAULT_ICON = "package"
DEFAULT_COLOR = "graphite"


@dataclass(frozen=True)
class Icon:
    key: str  # Lucide icon name, also the file name in transactions/icons/
    label: str


@dataclass(frozen=True)
class Color:
    key: str
    label: str
    fill: str  # solid color, light mode
    chip_bg: str  # translucent tint, light mode
    chip_text: str  # label on the tint, light mode
    fill_dark: str
    chip_bg_dark: str
    chip_text_dark: str


ICONS = (
    Icon("utensils", "Talheres"),
    Icon("car", "Carro"),
    Icon("house", "Casa"),
    Icon("gamepad-2", "Videogame"),
    Icon("pill", "Remédio"),
    Icon("package", "Caixa"),
    Icon("shopping-cart", "Carrinho de compras"),
    Icon("graduation-cap", "Formatura"),
    Icon("shirt", "Camiseta"),
    Icon("paw-print", "Pata"),
    Icon("luggage", "Mala"),
    Icon("gift", "Presente"),
    Icon("lightbulb", "Lâmpada"),
    Icon("smartphone", "Celular"),
    Icon("credit-card", "Cartão"),
    Icon("coffee", "Café"),
    Icon("dumbbell", "Haltere"),
    Icon("clapperboard", "Claquete"),
    Icon("baby", "Bebê"),
    Icon("receipt", "Recibo"),
)

COLORS = (
    Color("jade", "Jade", "#0f766e", "#e2efee", "#0f766e", "#0f766e", "#102b36", "#87bdb9"),
    Color("green", "Verde", "#039855", "#e1f3eb", "#027b45", "#039855", "#0d3231", "#7bc9a6"),
    Color("blue", "Azul", "#0086c9", "#e0f0f9", "#0070a7", "#0086c9", "#0d2e48", "#80c2e4"),
    Color("purple", "Roxo", "#7a5af8", "#efebfe", "#6f52e2", "#7a5af8", "#252552", "#bdadfc"),
    Color("pink", "Rosa", "#ee46bc", "#fde9f7", "#b5358f", "#ee46bc", "#3c2146", "#f69ddc"),
    Color("orange", "Laranja", "#ec4a0a", "#fde9e2", "#bf3c08", "#ec4a0a", "#3c2222", "#f5a07e"),
    Color("amber", "Âmbar", "#dc6803", "#fbede1", "#ac5202", "#dc6803", "#392821", "#ebac74"),
    Color("graphite", "Grafite", "#475467", "#e9eaed", "#475467", "#616c7d", "#202939", "#afb4bd"),
)

ICON_KEYS = tuple(i.key for i in ICONS)
COLOR_KEYS = tuple(c.key for c in COLORS)
ICON_BY_KEY = {i.key: i for i in ICONS}
COLOR_BY_KEY = {c.key: c for c in COLORS}
