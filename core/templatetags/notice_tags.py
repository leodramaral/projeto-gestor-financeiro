from django import template

register = template.Library()

# What each notification level looks like. The Tailwind classes are written out in full on purpose:
# Tailwind only generates a class it finds spelled out in a source file. The dark card is opaque (a
# `color-mix` of two opaque colors), so the cards of a toast stack do not show through each other.
NOTICE_LEVELS = {
    "success": {
        "name": "success",
        "icon_name": "circle-check",
        "title": "Tudo certo",
        "role": "status",
        "box": (
            "border-success-500 bg-success-50 "
            "dark:border-[color-mix(in_srgb,var(--color-success-500)_30%,var(--color-gray-900))] "
            "dark:bg-[color-mix(in_srgb,var(--color-success-500)_15%,var(--color-gray-900))]"
        ),
        "icon": "text-success-600 dark:text-success-400",
    },
    "error": {
        "name": "error",
        "icon_name": "circle-alert",
        "title": "Algo deu errado",
        "role": "alert",
        "box": (
            "border-error-500 bg-error-50 "
            "dark:border-[color-mix(in_srgb,var(--color-error-500)_30%,var(--color-gray-900))] "
            "dark:bg-[color-mix(in_srgb,var(--color-error-500)_15%,var(--color-gray-900))]"
        ),
        "icon": "text-error-600 dark:text-error-400",
    },
    "warning": {
        "name": "warning",
        "icon_name": "triangle-alert",
        "title": "Atenção",
        "role": "alert",
        "box": (
            "border-warning-500 bg-warning-50 "
            "dark:border-[color-mix(in_srgb,var(--color-warning-500)_30%,var(--color-gray-900))] "
            "dark:bg-[color-mix(in_srgb,var(--color-warning-500)_15%,var(--color-gray-900))]"
        ),
        "icon": "text-warning-600 dark:text-warning-400",
    },
    "info": {
        "name": "info",
        "icon_name": "info",
        "title": "Informação",
        "role": "status",
        "box": (
            "border-blue-light-500 bg-blue-light-50 "
            "dark:border-[color-mix(in_srgb,var(--color-blue-light-500)_30%,var(--color-gray-900))] "  # noqa: E501
            "dark:bg-[color-mix(in_srgb,var(--color-blue-light-500)_15%,var(--color-gray-900))]"
        ),
        "icon": "text-blue-light-600 dark:text-blue-light-400",
    },
}


@register.simple_tag
def notice_style(level):
    """The look of a notification level; an unknown level is shown as `info`."""
    return NOTICE_LEVELS.get(level, NOTICE_LEVELS["info"])
