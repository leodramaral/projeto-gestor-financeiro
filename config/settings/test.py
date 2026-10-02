"""Automated tests. Uses the same Postgres engine as production, via DATABASE_URL."""

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]
# Cheap hashing: password strength is irrelevant in tests and hashing dominates their runtime.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Emails go to django.core.mail.outbox; no mail service is needed.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "Gestor Financeiro <nao-responda@example.com>"
SITE_URL = "http://testserver"
