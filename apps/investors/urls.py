# apps/investors/urls.py

from django.urls import include, path
from .views import InvestorListView, InvestorCreateView
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

]