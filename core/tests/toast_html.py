"""Helpers to read the toast out of a rendered page (shared by the tests of every screen)."""

import re

TOAST = re.compile(r'<div hidden data-toast data-level="(\w+)">(.*?)</div>', re.DOTALL)
INERT = re.compile(r"<(noscript|template)\b.*?</\1>", re.DOTALL)


def toasts(html):
    """The (level, text) of each server message the page hands to the toast, in order."""
    return TOAST.findall(html)


def inline_alerts(html):
    """How many alerts sit in the page flow: outside the `<noscript>` fallback and the models."""
    return INERT.sub("", html).count("data-toast-text")


def noscript_fallback(html):
    """The static alerts inside `<noscript>`, shown only without JavaScript."""
    return "".join(re.findall(r"<noscript>(.*?)</noscript>", html, flags=re.DOTALL))
