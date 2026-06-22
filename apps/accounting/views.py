# apps/accounting/views.py

from django.views.generic import ListView
from .models import Transaction


class TransactionListView(ListView):
    model = Transaction
    template_name = 'accounting/transaction_list.html'
    context_object_name = 'transactions'