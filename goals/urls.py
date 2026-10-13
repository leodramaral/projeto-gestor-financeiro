from django.urls import path

from . import views

app_name = "goals"

urlpatterns = [
    path("", views.GoalListView.as_view(), name="list"),
    path("new/", views.GoalCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.GoalUpdateView.as_view(), name="update"),
    path("<int:pk>/progress/", views.GoalProgressView.as_view(), name="progress"),
    path("<int:pk>/delete/", views.GoalDeleteView.as_view(), name="delete"),
    path("<int:pk>/complete/", views.GoalCompleteView.as_view(), name="complete"),
    path("<int:pk>/reopen/", views.GoalReopenView.as_view(), name="reopen"),
]
