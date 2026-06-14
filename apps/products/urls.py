# products/urls.py

from django.urls import path
from .views import (
    ProductDetailView,
    ProductHomeView,
    MasterProductView,
    CategoryView,
    ProductVariantView,
    StockInView,
    StockMovementView
)

app_name = "products"

urlpatterns = [
        path(
        "",
        ProductHomeView.as_view(),
        name="products-home"
    ),

    path(
        "master-products/",
        MasterProductView.as_view(),
        name="master-products"
    ),
    path(
        "stock-movement/",
        StockMovementView.as_view(),
        name="stock-movement"
    ),

    path(
        "categories/",
        CategoryView.as_view(),
        name="categories"
    ),
    path(
    "<int:product_id>/variants/",
    ProductVariantView.as_view(),
    name="variants"
    ),
    path(
        "<int:product_id>/stock-in/",
        StockInView.as_view(),
        name="stock-in"
    ),
    path(
    "product-detail/<int:product_id>/",
    ProductDetailView.as_view(),
    name="product-detail"
),
]