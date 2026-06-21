from django import views
from django.urls import path

from apps.sales.views import (
    CustomerListView,
    CustomerCreateView,
    OrderDetailView,
    OrderListView,
    order_create,
    customer_search,
    variant_search
)

app_name = "sales"

urlpatterns = [

    # Orders
    path(
        "",
        OrderListView.as_view(),
        name="order_list",
    ),

    path(
        "create/",
        order_create,
        name="order_create",
    ),

    # Customers
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
    path(
        "customer-search/",
        customer_search,
        name="customer_search"
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

]