from django.urls import path

from .views import (
    DashboardView,
    HawalaReportView,
    ReportView,
    CustomerStatementView,
    CustomerStatementReportView,
    FactoryStatementView,
    hawala_summary,
    investor_summary,
    InvestorDetailView,
    InvestorSummaryView,
)

app_name = "core"

urlpatterns = [

    # Dashboard
    path(
        "",
        DashboardView.as_view(),
        name="dashboard",
    ),

    # Reports
    path(
        "reports/",
        ReportView.as_view(),
        name="reports",
    ),

    # Customer Statement Report - customer list
    path(
        "reports/customer-statements/",
        CustomerStatementReportView.as_view(),
        name="customer_statement_report",
    ),

    # Individual Customer Statement
    path(
        "customers/<int:customer_id>/statement/",
        CustomerStatementView.as_view(),
        name="customer_statement",
    ),

    # Factory Statement
    path(
        "factories/<int:factory_id>/statement/",
        FactoryStatementView.as_view(),
        name="factory_statement",
    ),

    # Investor Summary
    path(
        "reports/investments/",
        investor_summary,
        name="investor_summary",
    ),

    # Investor Detail
    path(
        "reports/investments/<int:investor_id>/",
        InvestorDetailView.as_view(),
        name="investor_detail",
    ),

    # Complete Investor Transaction Report
    path(
        "reports/investment-report/",
        InvestorSummaryView.as_view(),
        name="investor_report",
    ),
    path(
        "reports/hawala/",
        HawalaReportView.as_view(),
        name="hawala_report",
    ),
    path(
        "reports/hawala-summary/",
        hawala_summary,
        name="hawala_summary",
    ),
]