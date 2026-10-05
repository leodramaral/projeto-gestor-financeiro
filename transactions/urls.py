from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path("", views.TransactionListView.as_view(), name="list"),
    path("new/", views.TransactionCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.TransactionUpdateView.as_view(), name="update"),
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category-create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category-update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category-delete"),
    path("<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="delete"),
]
