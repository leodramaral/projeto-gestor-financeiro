import os
import subprocess
import sys

import pytest

REQUIRED = {
    "SECRET_KEY": "x",
    "DATABASE_URL": "postgres://u:p@localhost/db",
    "ALLOWED_HOSTS": "example.com",
    "EMAIL_HOST": "smtp.example.com",
    "EMAIL_HOST_USER": "user-secret",
    "EMAIL_HOST_PASSWORD": "password-secret",
    "DEFAULT_FROM_EMAIL": "Gestor <nao-responda@example.com>",
    "SITE_URL": "https://app.example.com",
}
EMAIL_VARS = [
    "EMAIL_HOST",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "DEFAULT_FROM_EMAIL",
    "SITE_URL",
]


def import_prod(env_vars):
    env = {"PATH": os.environ["PATH"], **env_vars}
    return subprocess.run(
        [sys.executable, "-c", "import config.settings.prod"],
        env=env,
        capture_output=True,
        text=True,
    )


def test_prod_imports_with_all_variables():
    result = import_prod(REQUIRED)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("missing", EMAIL_VARS)
def test_prod_fails_naming_the_missing_variable(missing):
    result = import_prod({k: v for k, v in REQUIRED.items() if k != missing})

    assert result.returncode != 0
    assert missing in result.stderr
    for secret in ("user-secret", "password-secret"):
        assert secret not in result.stderr


@pytest.mark.parametrize("empty", EMAIL_VARS)
def test_prod_fails_naming_the_empty_variable(empty):
    result = import_prod({**REQUIRED, empty: ""})

    assert result.returncode != 0
    assert empty in result.stderr
    for secret in ("user-secret", "password-secret"):
        assert secret not in result.stderr
