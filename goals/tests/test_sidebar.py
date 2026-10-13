import re

import pytest
from django.urls import reverse


def active_items(html):
    """Labels of the sidebar items marked with aria-current."""
    return re.findall(r'aria-current="page"[^>]*>.*?menu-item-text[^>]*>([^<]+)<', html, re.S)


@pytest.mark.parametrize("name", ["goals:list", "goals:create"])
def test_metas_item_is_active_in_goal_screens(logged, name):
    html = logged.get(reverse(name)).content.decode()
    assert active_items(html) == ["Metas"]


def test_metas_item_is_inactive_elsewhere(logged):
    html = logged.get(reverse("transactions:list")).content.decode()
    assert "Metas" in html
    assert active_items(html) == ["Lançamentos"]
