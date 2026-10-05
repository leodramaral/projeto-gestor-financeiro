from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

ZERO = Decimal("0.00")


class Transaction(models.Model):
    """An income or expense of a user. The amount is always positive; `kind` gives the sign."""

    class Kind(models.TextChoices):
        INCOME = "income", "Entrada"
        EXPENSE = "expense", "Despesa"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="usuário",
    )
    kind = models.CharField("tipo", max_length=7, choices=Kind.choices)
    amount = models.DecimalField("valor", max_digits=14, decimal_places=2)
    date = models.DateField("data")
    description = models.CharField("descrição", max_length=200)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "lançamento"
        verbose_name_plural = "lançamentos"
        ordering = ("-date", "-id")
        indexes = [models.Index(fields=["user", "-date", "-id"], name="transactions_user_date_idx")]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name="transactions_amount_gt_0"),
        ]

    def __str__(self):
        return f"{self.get_kind_display()} {self.amount} em {self.date}"


def current_balance(user):
    """Incomes - expenses over *all* the user's transactions (a starting balance is an income)."""
    totals = Transaction.objects.filter(user=user).aggregate(
        income=Coalesce(Sum("amount", filter=Q(kind=Transaction.Kind.INCOME)), ZERO),
        expense=Coalesce(Sum("amount", filter=Q(kind=Transaction.Kind.EXPENSE)), ZERO),
    )
    return totals["income"] - totals["expense"]
