"""Local development."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# Mailpit (docker-compose.yml): fake inbox at http://127.0.0.1:8025. No secrets, so not in .env.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mailpit"
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = "Gestor Financeiro <nao-responda@localhost>"
# Base of absolute links in emails sent outside a request.
SITE_URL = "http://127.0.0.1:8000"
