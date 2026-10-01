"""Automated tests. Uses the same Postgres engine as production, via DATABASE_URL."""

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]
# Cheap hashing: password strength is irrelevant in tests and hashing dominates their runtime.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
