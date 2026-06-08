# products/urls.py

from django.urls import path
from .views import (
    ProductHomeView,
    MasterProductView,
    CategoryView,
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
        "categories/",
        CategoryView.as_view(),
        name="categories"
    ),
]