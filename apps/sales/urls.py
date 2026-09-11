from django.urls import path

from apps.sales.views import (
    CustomerDeleteView,
    CustomerDetailView,
    CustomerListView,
    CustomerCreateView,
    CustomerUpdateView,
    OrderDetailView,
    OrderListView,
    OrderInvoiceView,
    order_create,
    customer_search,
    order_delete,
    variant_search,
)

app_name = "sales"

urlpatterns = [
    path("", OrderListView.as_view(), name="order_list"),

    path("create/", order_create, name="order_create"),

    path("customers/", CustomerListView.as_view(), name="customer_list"),

    path(
        "customers/create/",
        CustomerCreateView.as_view(),
        name="customer_create"
    ),

    path(
        "customer-search/",
        customer_search,
        name="customer_search"
    ),

    path(
        "customers/<int:pk>/update/",
        CustomerUpdateView.as_view(),
        name="customer_update"
    ),

    path(
        "customers/<int:pk>/delete/",
        CustomerDeleteView.as_view(),
        name="customer_delete"
    ),

    path(
        "variant-search/",
        variant_search,
        name="variant_search"
    ),

    path(
        "orders/<int:pk>/",
        OrderDetailView.as_view(),
        name="order_detail"
    ),

    path(
        "orders/<int:pk>/invoice/",
        OrderInvoiceView.as_view(),
        name="order_invoice"
    ),

    path(
        "customers/<int:pk>/",
        CustomerDetailView.as_view(),
        name="customer_detail"
    ),

    path(
        "orders/<int:pk>/delete/",
        order_delete,
        name="order_delete"
    ),
]