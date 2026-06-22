from django.urls import reverse_lazy

from .models import PurchaseOrder, PurchaseOrderItem
from .forms import PurchaseOrderItemForm
from .forms import (
    PurchaseOrderForm,
    PurchaseOrderItemFormSet
)

from django.views.generic import (
    ListView,
    CreateView
)
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .models import (
    Factory,
    PurchaseOrder
)

from .forms import (
    FactoryForm,
    PurchaseOrderForm
)


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


def factory_purchase_orders(request, factory_id):

    factory = get_object_or_404(
        Factory,
        pk=factory_id
    )

    purchase_orders = PurchaseOrder.objects.filter(
        factory=factory
    ).order_by("-id")

    context = {
        "factory": factory,
        "purchase_orders": purchase_orders,
    }

    return render(
        request,
        "purchases/factory_purchase_orders.html",
        context
    )


def purchase_order_create(request, factory_id):

    factory = get_object_or_404(
        Factory,
        pk=factory_id
    )

    if request.method == "POST":

        form = PurchaseOrderForm(request.POST)

        # no instance here yet
        formset = PurchaseOrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():

            purchase_order = form.save(commit=False)

            purchase_order.factory = factory

            if request.user.is_authenticated:
                purchase_order.created_by = request.user

            purchase_order.save()

            # NOW attach the formset to the saved PO
            formset.instance = purchase_order

            formset.save()

            subtotal = 0

            for item in purchase_order.items.all():

                subtotal += (
                    item.quantity *
                    item.price
                )

            purchase_order.subtotal = subtotal

            purchase_order.total = (
                subtotal +
                purchase_order.transport_tax_expenses_cost
            )

            purchase_order.save()

            return redirect(
                "purchases:factory_purchase_orders",
                factory_id=factory.id
            )

    else:

        form = PurchaseOrderForm()

        # for new PO page
        formset = PurchaseOrderItemFormSet()

    context = {
        "form": form,
        "formset": formset,
        "factory": factory,
    }

    return render(
        request,
        "purchases/purchase_order_form.html",
        context
    )




def purchase_order_detail(request, pk):

    purchase_order = get_object_or_404(
        PurchaseOrder.objects.select_related(
            "factory"
        ).prefetch_related(
            "items"
        ),
        pk=pk
    )

    context = {

        "purchase_order": purchase_order,

        "factory": purchase_order.factory,

        "items": purchase_order.items.all()

    }

    return render(
        request,
        "purchases/purchase_order_detail.html",
        context
    )