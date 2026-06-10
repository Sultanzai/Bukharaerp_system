from django.urls import path

from .views import (
    FactoryListView,
    FactoryCreateView
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

]