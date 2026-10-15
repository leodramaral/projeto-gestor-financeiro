from django.contrib import admin

from .models import Usage


@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ("user", "day", "tokens")
    list_filter = ("day",)
    search_fields = ("user__email",)
