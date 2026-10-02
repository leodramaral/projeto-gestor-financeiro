from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("signup/done/", views.SignupDoneView.as_view(), name="signup_done"),
    path("login/", views.SignInView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("confirm/resend/", views.ResendConfirmationView.as_view(), name="resend"),
    path(
        "confirm/resend/done/",
        views.ResendConfirmationDoneView.as_view(),
        name="resend_done",
    ),
    path("confirm/<uidb64>/<token>/", views.ConfirmEmailView.as_view(), name="confirm"),
]
