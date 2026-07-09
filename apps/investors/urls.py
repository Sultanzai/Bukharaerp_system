# apps/investors/urls.py

from django.urls import include, path
from .views import InvestorDeleteView, InvestorListView, InvestorCreateView, InvestorTransactionDeleteView, InvestorUpdateView
from .views import (
    InvestorListView,
    InvestorCreateView,
    InvestorDetailView,
    InvestorTransactionCreateView,
)

urlpatterns = [

    path(
        '',
        InvestorListView.as_view(),
        name='investor_list'
    ),

    path(
        'create/',
        InvestorCreateView.as_view(),
        name='investor_create'
    ),
    path(
        '<int:pk>/',
        InvestorDetailView.as_view(),
        name='investor_detail'
    ),
    path(
    '<int:investor_id>/transaction/add/',
    InvestorTransactionCreateView.as_view(),
    name='investor_transaction_create'
    ),
    path(
        'transaction/<int:pk>/delete/',
        InvestorTransactionDeleteView.as_view(),
        name='transaction_delete'
    ),
    path(
        "<int:pk>/update/",
        InvestorUpdateView.as_view(),
        name="investor_update",
    ),

    path(
        "<int:pk>/delete/",
        InvestorDeleteView.as_view(),
        name="investor_delete",
    ),
]