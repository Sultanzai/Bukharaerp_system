from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView
)

from .models import Factory
from .forms import FactoryForm


class FactoryListView(ListView):

    model = Factory

    template_name = "purchases/index.html"

    context_object_name = "factories"

    queryset = Factory.objects.order_by("-id")


class FactoryCreateView(CreateView):

    model = Factory

    form_class = FactoryForm

    template_name = "purchases/create.html"

    success_url = reverse_lazy(
        "purchases:factories"
    )