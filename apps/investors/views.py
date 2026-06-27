# apps/investors/views.py

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.db.models import Q
from .models import Investor
from .forms import InvestorForm
from django.db.models import Sum
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.views.generic import ListView

from .models import Investor
from .forms import InvestorTransactionForm
from .models import Investor, InvestorTransaction


class InvestorListView(ListView):

    model = Investor
    template_name = 'investors/investor_list.html'
    context_object_name = 'investors'

    def get_queryset(self):

        investors = Investor.objects.all()

        for investor in investors:

            investor.total_invested = investor.transactions.filter(
                type='investment'
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0

            investor.total_withdrawn = investor.transactions.filter(
                type='withdrawal'
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0

            investor.total_profit = investor.transactions.filter(
                type='profit_distribution'
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0

            investor.balance = (
                investor.total_invested
                + investor.total_profit
                - investor.total_withdrawn
            )

        return investors

class InvestorCreateView(CreateView):

    model = Investor

    form_class = InvestorForm

    template_name = 'investors/investor_form.html'

    success_url = reverse_lazy('investor_list')


class InvestorDetailView(DetailView):

    model = Investor

    template_name = 'investors/investor_detail.html'

    context_object_name = 'investor'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        investor = self.object

        investment_total = investor.transactions.filter(
            type='investment'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        withdrawal_total = investor.transactions.filter(
            type='withdrawal'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        profit_total = investor.transactions.filter(
            type='profit_distribution'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        balance = (
            investment_total
            + profit_total
            - withdrawal_total
        )

        context['transactions'] = investor.transactions.all()

        context['investment_total'] = investment_total
        context['withdrawal_total'] = withdrawal_total
        context['profit_total'] = profit_total
        context['balance'] = balance

        return context
    

class InvestorTransactionCreateView(CreateView):

    model = InvestorTransaction

    form_class = InvestorTransactionForm

    template_name = 'investors/investor_transaction_form.html'

    def get_investor(self):

        return get_object_or_404(
            Investor,
            pk=self.kwargs['investor_id']
        )

    def get_current_balance(self):

        investor = self.get_investor()

        investment = investor.transactions.filter(
            type='investment'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        withdrawal = investor.transactions.filter(
            type='withdrawal'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        profit = investor.transactions.filter(
            type='profit_distribution'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        return investment + profit - withdrawal

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs['current_balance'] = self.get_current_balance()

        return kwargs

    def form_valid(self, form):

        form.instance.investor = self.get_investor()

        return super().form_valid(form)

    def get_success_url(self):

        return reverse_lazy(
            'investor_detail',
            kwargs={
                'pk': self.kwargs['investor_id']
            }
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['investor'] = self.get_investor()

        context['current_balance'] = self.get_current_balance()

        return context