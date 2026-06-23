# apps/accounting/views.py

from django.views.generic import ListView
from .models import Transaction
from django.views.generic import DetailView

from .models import Transaction
from apps.sales.models import Order
from apps.purchases.models import PurchaseOrder
from apps.sales.models import Customer
from apps.purchases.models import Factory
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal
from django.db.models import Sum
from .models import Transaction
from .models import PaymentRecord
from .forms import PaymentRecordForm

class TransactionListView(ListView):
    model = Transaction
    template_name = 'accounting/transaction_list.html'
    context_object_name = 'transactions'


class TransactionDetailView(DetailView):
    model = Transaction
    template_name = 'accounting/transaction_detail.html'
    context_object_name = 'transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        transaction = self.object

        party = None
        document = None

        if transaction.party_type == 'customer':
            party = Customer.objects.get(pk=transaction.party_id)

        elif transaction.party_type == 'factory':
            party = Factory.objects.get(pk=transaction.party_id)

        if transaction.reference_type == 'customer_order':
            document = Order.objects.get(pk=transaction.reference_id)

        elif transaction.reference_type == 'purchase_order':
            document = PurchaseOrder.objects.get(pk=transaction.reference_id)

        context['party'] = party
        context['document'] = document
        context['payments'] = transaction.payments.all()

        return context



# Add Payment view
def payment_create(request, transaction_id):

    transaction = get_object_or_404(
        Transaction,
        pk=transaction_id
    )

    total_paid = (
        transaction.payments.aggregate(
            total=Sum('paid_amount')
        )['total']
        or Decimal('0')
    )

    remaining_amount = transaction.amount - total_paid

    if request.method == 'POST':

        form = PaymentRecordForm(
            request.POST,
            remaining_amount=remaining_amount
        )

        if form.is_valid():

            payment = form.save(commit=False)

            payment.transaction = transaction

            payment.save()

            total_paid = (
                transaction.payments.aggregate(
                    total=Sum('paid_amount')
                )['total']
                or Decimal('0')
            )

            remaining_amount = transaction.amount - total_paid

            if remaining_amount <= Decimal('0'):
                transaction.status = 'completed'
            else:
                transaction.status = 'pending'

            transaction.save()

            return redirect(
                'transaction_detail',
                pk=transaction.id
            )

    else:

        form = PaymentRecordForm(
            remaining_amount=remaining_amount
        )

    context = {
        'transaction': transaction,
        'form': form,
        'total_paid': total_paid,
        'remaining_amount': remaining_amount,
    }

    return render(
        request,
        'accounting/payment_form.html',
        context
    )