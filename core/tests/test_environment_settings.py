import json
import os
import subprocess
import sys

import pytest

# Distinctive values, so a leak of any of them into the error output is easy to spot.
SECRET_KEY = "secret-key-value"
DATABASE_URL = "postgres://db-user:db-password@localhost/db"
BASE_ENV = {"SECRET_KEY": SECRET_KEY, "DATABASE_URL": DATABASE_URL}
PROD_ENV = {
    **BASE_ENV,
    "ALLOWED_HOSTS": "app.example.com,www.example.com",
    "EMAIL_HOST": "smtp.example.com",
    "EMAIL_HOST_USER": "user",
    "EMAIL_HOST_PASSWORD": "password",
    "DEFAULT_FROM_EMAIL": "Gestor <nao-responda@example.com>",
    "SITE_URL": "https://app.example.com",
}
ENVIRONMENTS = {
    "config.settings.dev": BASE_ENV,
    "config.settings.test": BASE_ENV,
    "config.settings.prod": PROD_ENV,
}
SECURITY_SETTINGS = [
    "DEBUG",
    "ALLOWED_HOSTS",
    "SESSION_COOKIE_SECURE",
    "CSRF_COOKIE_SECURE",
    "SECURE_HSTS_SECONDS",
    "SECURE_SSL_REDIRECT",
]


def start(module, env_vars, code=""):
    """Start Django with the given settings module in a fresh process with only these variables."""
    env = {"PATH": os.environ["PATH"], "DJANGO_SETTINGS_MODULE": module, **env_vars}
    # `code` only ever comes from this module's own constants, never from outside input.
    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", f"import django; django.setup(); {code}"],
        env=env,
        capture_output=True,
        text=True,
    )


def read_security_settings(module, env_vars):
    code = (
        "import json; from django.conf import settings; "
        f"print(json.dumps({{name: getattr(settings, name) for name in {SECURITY_SETTINGS!r}}}))"
    )
    result = start(module, env_vars, code)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize("module", ENVIRONMENTS)
@pytest.mark.parametrize("missing", ["SECRET_KEY", "DATABASE_URL"])
def test_startup_fails_naming_the_missing_variable_without_values(module, missing):
    result = start(module, {k: v for k, v in ENVIRONMENTS[module].items() if k != missing})

    assert result.returncode != 0
    # The last stderr line is the exception itself; the traceback above it repeats the source line,
    # which names the variable whatever the message says.
    error = result.stderr.strip().splitlines()[-1]
    assert error == (
        f"django.core.exceptions.ImproperlyConfigured: Set the {missing} environment variable"
    )
    for value in (SECRET_KEY, "db-password"):
        assert value not in result.stderr


def test_production_turns_debug_off_and_hardens_cookies_and_transport():
    settings = read_security_settings("config.settings.prod", PROD_ENV)

    assert settings == {
        "DEBUG": False,
        "ALLOWED_HOSTS": ["app.example.com", "www.example.com"],
        "SESSION_COOKIE_SECURE": True,
        "CSRF_COOKIE_SECURE": True,
        "SECURE_HSTS_SECONDS": 31536000,
        "SECURE_SSL_REDIRECT": True,
    }


def test_production_reads_allowed_hosts_only_from_the_environment():
    result = start(
        "config.settings.prod", {k: v for k, v in PROD_ENV.items() if k != "ALLOWED_HOSTS"}
    )

    assert result.returncode != 0
    assert result.stderr.strip().splitlines()[-1] == (
        "django.core.exceptions.ImproperlyConfigured: Set the ALLOWED_HOSTS environment variable"
    )


def test_development_turns_debug_on():
    assert read_security_settings("config.settings.dev", BASE_ENV)["DEBUG"] is True
