from django.urls import path

from apps.sales.views import (
    CustomerListView,
    CustomerCreateView,
)

app_name = "sales"

urlpatterns = [
    path(
        "customers/",
        CustomerListView.as_view(),
        name="customer_list",
    ),

    path(
        "customers/create/",
        CustomerCreateView.as_view(),
        name="customer_create",
    ),
]