# apps/accounting/urls.py

from django.urls import path

from apps.accounting import views
from .views import TransactionListView, TransactionDetailView


urlpatterns = [
    path(
        'transactions/',
        TransactionListView.as_view(),
        name='transaction_list'
    ),
    path(
        'transactions/<int:pk>/',
        TransactionDetailView.as_view(),
        name='transaction_detail'
    ),

    path(
        'transactions/<int:transaction_id>/payment/add/',
        views.payment_create,
        name='payment_create'
    ),
]