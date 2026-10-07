from django.urls import path

from .views import CategoriesView, FlowView, OverviewView, TransactionsTabView

urlpatterns = [
    path("", OverviewView.as_view(), name="home"),
    path("dashboard/categories/", CategoriesView.as_view(), name="dashboard_categories"),
    path("dashboard/flow/", FlowView.as_view(), name="dashboard_flow"),
    path("dashboard/transactions/", TransactionsTabView.as_view(), name="dashboard_transactions"),
]
