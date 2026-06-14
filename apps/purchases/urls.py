from django.urls import path

from .views import (
    FactoryListView,
    FactoryCreateView,
    factory_purchase_orders,
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
        "factory/<int:factory_id>/purchase-orders/",
        factory_purchase_orders,
        name="factory_purchase_orders"
    ),

    path(
        "factory/<int:factory_id>/purchase-orders/create/",
        purchase_order_create,
        name="purchase_order_create"
    ),

]