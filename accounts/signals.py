from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from . import throttle


@receiver(user_logged_in)
def reset_throttle_on_login(sender, request, user, **kwargs):
    if user and getattr(user, "email", None):
        throttle.reset(user.email)
