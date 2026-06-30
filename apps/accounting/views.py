# apps/accounting/views.py

from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import ListView, CreateView
from apps.sales.models import Order
from apps.purchases.models import PurchaseOrder
from apps.sales.models import Customer
from apps.purchases.models import Factory
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal
from django.db.models import Sum
from .models import HawalaTransaction, Transaction
from .models import PaymentRecord
from .forms import HawalaTransactionForm, PaymentRecordForm

from .forms import HawalaAccountForm
from .models import HawalaAccount

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

class HawalaAccountListView(ListView):

    model = HawalaAccount
    template_name = "accounting/hawala_list.html"
    context_object_name = "accounts"

    def get_queryset(self):

        accounts = HawalaAccount.objects.all()

        for account in accounts:

            debit = (
                account.transactions.filter(status="completed").aggregate(
                    total=Sum("debit")
                )["total"]
                or Decimal("0.00")
            )

            credit = (
                account.transactions.filter(status="completed").aggregate(
                    total=Sum("credit")
                )["total"]
                or Decimal("0.00")
            )

            # Balance = Credit - Debit
            account.balance = credit - debit

        return accounts
class HawalaAccountCreateView(CreateView):

    model = HawalaAccount

    form_class = HawalaAccountForm

    template_name = "accounting/hawala_form.html"

    success_url = reverse_lazy("hawala_list")





class HawalaDetailView(DetailView):

    model = HawalaAccount

    template_name = "accounting/hawala_detail.html"

    context_object_name = "account"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        account = self.object

        total_credit = account.transactions.aggregate(
            total=Sum("credit")
        )["total"] or 0

        total_debit = account.transactions.aggregate(
            total=Sum("debit")
        )["total"] or 0

        balance = total_credit - total_debit

        context["transactions"] = account.transactions.all()

        context["total_debit"] = total_debit

        context["total_credit"] = total_credit

        context["balance"] = balance

        return context
    

class HawalaTransactionCreateView(CreateView):

    model = HawalaTransaction

    form_class = HawalaTransactionForm

    template_name = "accounting/hawala_transaction_form.html"

    def get_account(self):

        return get_object_or_404(

            HawalaAccount,

            pk=self.kwargs["account_id"]

        )

    def form_valid(self, form):

        form.instance.hawala_account = self.get_account()

        if form.instance.credit is None:
            form.instance.credit = Decimal("0")

        if form.instance.debit is None:
            form.instance.debit = Decimal("0")

        return super().form_valid(form)

    def get_success_url(self):

        return reverse_lazy(

            "hawala_detail",

            kwargs={

                "pk": self.kwargs["account_id"]

            }

        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["account"] = self.get_account()

        return context