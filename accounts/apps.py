from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        from django.contrib import admin

        from . import signals  # noqa: F401
        from .forms import AdminLoginForm

        admin.site.login_form = AdminLoginForm
