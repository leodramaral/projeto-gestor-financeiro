"""Settings shared by every environment. Not an environment itself."""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# No default on purpose: the app must fail at startup when these are missing.
SECRET_KEY = env("SECRET_KEY")
DATABASES = {"default": env.db("DATABASE_URL")}

INSTALLED_APPS = [
    "accounts",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "transactions",
    "goals",
    "assistant",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Seconds before a stuck SMTP connection gives up, so a slow server cannot hang a request.
EMAIL_TIMEOUT = 10

AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "accounts:login"

# Without "remember me" the session ends when the browser closes; with it, it lasts this long.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_REMEMBER_SECONDS = 60 * 60 * 24 * 30
# Lifetime of account confirmation links.
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24 * 3
# Lifetime of password reset links: shorter, since they grant access to the account.
PASSWORD_RESET_LINK_TIMEOUT = 60 * 60

# Consecutive wrong-credential logins for one email before it is locked, and for how long.
LOGIN_MAX_FAILED_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 60 * 15

# Transactions shown per page in the list.
TRANSACTIONS_PER_PAGE = 20

# Assistant: an OpenAI-compatible provider (Groq by default). The key has no usable default: without
# it the assistant page says it is unavailable and the rest of the app keeps working.
LLM_API_KEY = env("LLM_API_KEY", default="")
LLM_BASE_URL = env("LLM_BASE_URL", default="https://api.groq.com/openai/v1")
LLM_MODEL = env("LLM_MODEL", default="openai/gpt-oss-120b")
# Tokens each user can spend per day (the provider's daily quota is shared by the whole key).
LLM_DAILY_TOKEN_LIMIT = env.int("LLM_DAILY_TOKEN_LIMIT", default=40000)
# Seconds to wait for the provider before giving up.
LLM_TIMEOUT_SECONDS = env.int("LLM_TIMEOUT_SECONDS", default=20)
