import pytest
from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message


@pytest.mark.parametrize(
    ("level", "tag"),
    [
        (constants.SUCCESS, "success"),
        (constants.ERROR, "error"),
        (constants.WARNING, "warning"),
        (constants.INFO, "info"),
        (constants.DEBUG, "info"),
    ],
)
def test_every_django_level_maps_to_one_of_the_four_toast_levels(level, tag):
    assert Message(level, "texto").level_tag == tag


def test_a_custom_level_has_no_tag_so_the_toast_falls_back_to_info():
    assert Message(99, "texto").level_tag == ""
