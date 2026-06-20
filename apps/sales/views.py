from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic import CreateView

from apps.sales.models import Customer
from apps.sales.forms import CustomerForm


class CustomerListView(ListView):
    model = Customer
    template_name = "sales/customer_list.html"
    context_object_name = "customers"


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "sales/customer_form.html"
    success_url = reverse_lazy("sales:customer_list")