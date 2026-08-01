from django.urls import path

from apps.core import views

from .views import (
    FactoryDeleteView,
    FactoryListView,
    FactoryCreateView,
    FactoryUpdateView,
    factory_purchase_orders,
    purchase_order_delete,
    purchase_order_detail,
    purchase_order_create,
)

app_name = "purchases"

urlpatterns = [

    path(
        "",
        FactoryListView.as_view(),
        name="factories"
    ),

    path(
        "create/",
        FactoryCreateView.as_view(),
        name="factory-create"
    ),

    path(
        "factories/<int:pk>/update/",
        FactoryUpdateView.as_view(),
        name="factory-update",
    ),

    path(
        "factories/<int:pk>/delete/",
        FactoryDeleteView.as_view(),
        name="factory-delete",
    ),


    path(
        "factory/<int:factory_id>/purchase-orders/",
        factory_purchase_orders,
        name="factory_purchase_orders"
    ),

    path(
        "factory/<int:factory_id>/purchase-orders/create/",
        purchase_order_create,
        name="purchase_order_create"
    ),

    path(
        "purchase-orders/<int:pk>/",
        purchase_order_detail,
        name="purchase_order_detail"
    ),

    path(
        "purchase-orders/<int:pk>/delete/",
        purchase_order_delete,
        name="purchase_order_delete",
    ),
]