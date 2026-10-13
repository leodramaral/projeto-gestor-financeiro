from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

ZERO = Decimal("0.00")


class GoalQuerySet(models.QuerySet):
    def active(self):
        """Open goals: the nearest deadline first, those without one last, then the newest."""
        return self.filter(completed_at__isnull=True).order_by(
            F("deadline").asc(nulls_last=True), "-created_at", "-id"
        )

    def completed(self):
        """Finished goals, the latest completion first."""
        return self.filter(completed_at__isnull=False).order_by("-completed_at", "-id")


class Goal(models.Model):
    """A savings goal of a user. `saved_amount` is the total set aside, not a sum of deposits."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goals",
        verbose_name="usuário",
    )
    name = models.CharField("nome", max_length=60)
    target_amount = models.DecimalField("valor-alvo", max_digits=14, decimal_places=2)
    saved_amount = models.DecimalField(
        "valor já guardado", max_digits=14, decimal_places=2, default=ZERO
    )
    deadline = models.DateField("prazo", null=True, blank=True)
    completed_at = models.DateTimeField("concluída em", null=True, blank=True)
    created_at = models.DateTimeField("criada em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizada em", auto_now=True)

    objects = GoalQuerySet.as_manager()

    class Meta:
        verbose_name = "meta"
        verbose_name_plural = "metas"
        indexes = [models.Index(fields=["user", "completed_at"], name="goals_user_completed_idx")]
        constraints = [
            models.CheckConstraint(condition=Q(target_amount__gt=0), name="goals_target_gt_0"),
            models.CheckConstraint(condition=Q(saved_amount__gte=0), name="goals_saved_gte_0"),
        ]

    def __str__(self):
        return self.name

    @property
    def is_completed(self):
        return self.completed_at is not None

    @property
    def is_overdue(self):
        """An open goal whose deadline has passed (today is still on time)."""
        return (
            not self.is_completed
            and self.deadline is not None
            and self.deadline < timezone.localdate()
        )

    @property
    def progress_percent(self):
        """Whole percent saved/target, floored (99,9 % shows 99) and capped at 100."""
        return min(100, int(self.saved_amount * 100 // self.target_amount))

    def complete(self):
        self.completed_at = timezone.now()
        self.save(update_fields=["completed_at", "updated_at"])

    def reopen(self):
        self.completed_at = None
        self.save(update_fields=["completed_at", "updated_at"])
