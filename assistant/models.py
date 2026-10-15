from django.conf import settings
from django.db import models
from django.db.models import F
from django.utils import timezone


class Usage(models.Model):
    """Tokens a user spent with the assistant on one day (local time). The only thing it keeps."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assistant_usages",
        verbose_name="usuário",
    )
    day = models.DateField("dia")
    tokens = models.PositiveIntegerField("tokens usados", default=0)

    class Meta:
        verbose_name = "uso do assistente"
        verbose_name_plural = "usos do assistente"
        constraints = [
            models.UniqueConstraint(fields=["user", "day"], name="assistant_usage_user_day_uniq"),
        ]

    def __str__(self):
        return f"{self.user} {self.day}: {self.tokens}"


def tokens_used_today(user):
    """Tokens the user has spent today, in the local day."""
    used = Usage.objects.filter(user=user, day=timezone.localdate()).values_list(
        "tokens", flat=True
    )
    return used.first() or 0


def reserve_tokens(user, amount, limit):
    """Reserves `amount` tokens of today's usage before the provider is called, so parallel
    questions cannot all pass a check made before any of them has spent anything. Returns the
    usage row's pk, or None when the user is already at `limit`; `settle_tokens` fixes the
    difference afterwards."""
    usage, _ = Usage.objects.get_or_create(user=user, day=timezone.localdate())
    reserved = Usage.objects.filter(pk=usage.pk, tokens__lt=limit).update(
        tokens=F("tokens") + amount
    )
    return usage.pk if reserved else None


def settle_tokens(pk, reserved, spent):
    """Replaces the `reserved` tokens of the usage row `pk` by what was `spent`."""
    if spent != reserved:
        Usage.objects.filter(pk=pk).update(tokens=F("tokens") + spent - reserved)


def add_tokens(user, tokens):
    """Add `tokens` to today's usage of `user`; the sum is done by the database, so concurrent
    questions of the same user do not lose any."""
    if tokens <= 0:
        return
    usage, _ = Usage.objects.get_or_create(user=user, day=timezone.localdate())
    Usage.objects.filter(pk=usage.pk).update(tokens=F("tokens") + tokens)
