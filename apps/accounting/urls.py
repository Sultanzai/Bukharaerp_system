# apps/accounting/urls.py

from django.urls import path

from apps.accounting import views
from .views import HawalaAccountListView, HawalaDetailView, HawalaTransactionCreateView, TransactionListView, TransactionDetailView, HawalaAccountCreateView


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
    path(
        "hawala/",
        HawalaAccountListView.as_view(),
        name="hawala_list"
    ),

    path(
        "hawala/create/",
        HawalaAccountCreateView.as_view(),
        name="hawala_create"
    ),
    path(
        "hawala/<int:pk>/",
        HawalaDetailView.as_view(),
        name="hawala_detail",
    ),
    path(
        "hawala/<int:account_id>/transaction/add/",
        HawalaTransactionCreateView.as_view(),
        name="hawala_transaction_create",
    ),
]