from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def normalize_email(self, email):
        """Lowercase the whole address: login and uniqueness ignore case."""
        return (email or "").strip().lower()

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # Admins created from the command line skip the confirmation email.
        extra_fields.setdefault("email_confirmed_at", timezone.now())
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("A superuser must have is_staff and is_superuser set to True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Account identified by email. `email_confirmed_at` is null until the email is confirmed."""

    email = models.EmailField("e-mail", max_length=254, unique=True)
    name = models.CharField("nome", max_length=150)
    email_confirmed_at = models.DateTimeField("e-mail confirmado em", null=True, blank=True)
    is_active = models.BooleanField("ativo", default=True)
    is_staff = models.BooleanField("acesso ao admin", default=False)
    date_joined = models.DateTimeField("cadastrado em", default=timezone.now)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_unique"),
        ]

    def __str__(self):
        return self.email

    @property
    def is_email_confirmed(self):
        return self.email_confirmed_at is not None

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.split(" ")[0] if self.name else self.email

    def clean(self):
        super().clean()
        self.email = type(self).objects.normalize_email(self.email)
