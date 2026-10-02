"""Production. Everything environment-specific comes from environment variables."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import env


def required_env(name):
    """Return the variable, failing at startup if it is unset or empty. Never echoes the value."""
    value = env(name)
    if not value.strip():
        raise ImproperlyConfigured(f"Set the {name} environment variable.")
    return value


DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# TLS terminates at the reverse proxy in front of the container.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email over SMTP. No defaults for the credentials, sender and base URL: startup fails without them.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = required_env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = required_env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = required_env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = required_env("DEFAULT_FROM_EMAIL")
# Base of absolute links in emails sent outside a request, e.g. https://app.example.com
SITE_URL = required_env("SITE_URL")
