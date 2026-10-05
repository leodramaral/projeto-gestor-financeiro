from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Case, F, Q, Sum, When
from django.db.models.functions import Coalesce, Lower

from .appearance import DEFAULT_COLOR, DEFAULT_ICON

ZERO = Decimal("0.00")
OTHER_CATEGORY_NAME = "Outros"


class CategoryQuerySet(models.QuerySet):
    def for_user(self, user):
        """What a user can pick: the default categories (seeding order), then their own by name."""
        default_order = Case(When(user__isnull=True, then=F("id")), default=0)
        return self.filter(Q(user=user) | Q(user__isnull=True)).order_by(
            F("user").asc(nulls_first=True), default_order, Lower("name")
        )


class Category(models.Model):
    """A label for expenses. `user` is null for the default categories shared by everyone."""

    name = models.CharField("nome", max_length=40)
    icon = models.CharField("ícone", max_length=24, default=DEFAULT_ICON)
    color = models.CharField("cor", max_length=16, default=DEFAULT_COLOR)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="categories",
        verbose_name="usuário",
    )

    objects = CategoryQuerySet.as_manager()

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        constraints = [
            models.UniqueConstraint(Lower("name"), "user", name="categories_user_name_uniq"),
            # A unique index treats NULLs as distinct, so the default ones need their own rule.
            models.UniqueConstraint(
                Lower("name"),
                condition=Q(user__isnull=True),
                name="categories_default_name_uniq",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def is_default(self):
        return self.user_id is None

    @classmethod
    def other(cls):
        """The default "Outros" category, where orphaned expenses go."""
        return cls.objects.get(user__isnull=True, name=OTHER_CATEGORY_NAME)


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
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="categoria",
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "lançamento"
        verbose_name_plural = "lançamentos"
        ordering = ("-date", "-id")
        indexes = [models.Index(fields=["user", "-date", "-id"], name="transactions_user_date_idx")]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name="transactions_amount_gt_0"),
            # Only incomes go without a category.
            models.CheckConstraint(
                condition=Q(kind="income") | Q(category__isnull=False),
                name="transactions_expense_has_category",
            ),
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
