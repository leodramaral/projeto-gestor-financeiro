import math

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm, SetPasswordForm

from . import throttle

User = get_user_model()

INPUT_CLASS = (
    "h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm "
    "text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 "
    "focus:ring-3 focus:ring-brand-500/10 focus:outline-hidden dark:border-gray-700 "
    "dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
)
CHECKBOX_CLASS = "h-4 w-4 rounded border-gray-300 text-brand-500"


class StyledFormMixin:
    """Gives every widget the project's input styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            is_checkbox = isinstance(field.widget, forms.CheckboxInput)
            field.widget.attrs["class"] = CHECKBOX_CLASS if is_checkbox else INPUT_CLASS


class SignupForm(StyledFormMixin, BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The parent focuses the email; the form reads top to bottom, so start at the name.
        self.fields["email"].widget.attrs.pop("autofocus", None)
        self.fields["name"].widget.attrs.update({"autocomplete": "name", "autofocus": True})
        self.fields["email"].widget.attrs["autocomplete"] = "email"
        # The rules are shown by a live checklist in the template, not as Django's static list.
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        self.fields["password1"].widget.attrs["x-model"] = "password1"
        self.fields["password2"].widget.attrs["x-model"] = "password2"
        self.fields["email"].required = True
        self.fields["password1"].label = "Senha"
        self.fields["password2"].label = "Confirmação da senha"

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"])
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Este e-mail já está cadastrado.", code="email_already_registered"
            )
        return email


class LoginForm(StyledFormMixin, AuthenticationForm):
    username = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"autofocus": True}))
    remember_me = forms.BooleanField(label="Lembrar de mim", required=False)

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "E-mail ou senha incorretos.",
        "unconfirmed": "Confirme seu e-mail para entrar. Procure a mensagem de confirmação.",
        "locked": "Muitas tentativas de login. Tente novamente em %(minutes)d %(unit)s.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unconfirmed = False
        self.fields["password"].widget.attrs["autocomplete"] = "current-password"

    def clean_username(self):
        return User.objects.normalize_email(self.cleaned_data["username"])

    def clean(self):
        email = self.cleaned_data.get("username")
        if email:
            remaining = throttle.lock_remaining(email)
            if remaining is not None:
                minutes = max(1, math.ceil(remaining.total_seconds() / 60))
                raise forms.ValidationError(
                    self.error_messages["locked"],
                    code="locked",
                    params={"minutes": minutes, "unit": "minuto" if minutes == 1 else "minutos"},
                )
        try:
            return super().clean()
        except forms.ValidationError as error:
            if error.code == "invalid_login":
                throttle.register_failure(email)
            raise

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_email_confirmed:
            self.unconfirmed = True
            raise forms.ValidationError(self.error_messages["unconfirmed"], code="unconfirmed")


class ResendConfirmationForm(StyledFormMixin, forms.Form):
    email = forms.EmailField(label="E-mail")

    def clean_email(self):
        return User.objects.normalize_email(self.cleaned_data["email"])


class PasswordResetRequestForm(ResendConfirmationForm):
    """Same single email field as the confirmation resend."""


class SetNewPasswordForm(StyledFormMixin, SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Nova senha"
        self.fields["new_password2"].label = "Confirmação da nova senha"
        self.fields["new_password1"].help_text = ""
        self.fields["new_password2"].help_text = ""
        self.fields["new_password1"].widget.attrs.update(
            {"autocomplete": "new-password", "autofocus": True}
        )
        self.fields["new_password2"].widget.attrs["autocomplete"] = "new-password"
