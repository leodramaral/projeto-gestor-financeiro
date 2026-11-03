import os

import pytest


@pytest.fixture(scope="session")
def django_db_modify_db_settings(django_db_modify_db_settings_parallel_suffix):
    """Give each mutation-testing process its own test database.

    mutmut forks one process per mutant, and each one runs a pytest session that creates and
    drops the test database. With a shared name, parallel workers drop each other's database and
    the failure is counted as a killed mutant. mutmut sets `MUTANT_UNDER_TEST`; a regular pytest
    run does not, so it keeps the usual name.
    """
    if "MUTANT_UNDER_TEST" not in os.environ:
        return
    from django.conf import settings

    db_settings = settings.DATABASES["default"]
    test_name = db_settings.get("TEST", {}).get("NAME") or f"test_{db_settings['NAME']}"
    db_settings.setdefault("TEST", {})["NAME"] = f"{test_name}_mut{os.getpid()}"
