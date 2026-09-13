# apps/core/urls.py

from django.urls import path
from .views import DashboardView, FactoryStatementView, ReportView
from .views import CustomerStatementView

app_name = "core"

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path("reports/", ReportView.as_view(), name="reports"),
    path(
        "customers/<int:customer_id>/statement/",
        CustomerStatementView.as_view(),
        name="customer_statement",
    ),
    path(
    "factories/<int:factory_id>/statement/",
    FactoryStatementView.as_view(),
    name="factory_statement",
),

]