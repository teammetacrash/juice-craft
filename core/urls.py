from django.urls import path
from . import views

urlpatterns = [
    path("healthz/", views.health_view, name="health"),
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("billing/", views.billing, name="billing"),
    path("inventory/", views.inventory, name="inventory"),
    path("stock/", views.stock, name="stock"),
    path("prepared/", views.prepared, name="prepared"),
    path("wastage/", views.wastage, name="wastage"),
    path("expenses/", views.expenses, name="expenses"),
    path("reports/", views.reports, name="reports"),
    path("settings/", views.settings_page, name="settings"),
    path("api/<str:action>/", views.api_dispatch, name="api_dispatch"),
]
