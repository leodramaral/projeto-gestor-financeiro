from django.urls import path

from . import views

app_name = "assistant"

urlpatterns = [
    path("", views.ChatView.as_view(), name="chat"),
    path("nova/", views.NewConversationView.as_view(), name="new"),
]
