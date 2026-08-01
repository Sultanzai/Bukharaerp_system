from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Sum, Q, DecimalField
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import UpdateView
from apps.accounting.models import Transaction, PaymentRecord
from apps.products.models import ProductVariant, StockMovement
from apps.sales.forms import CustomerForm, OrderForm
from apps.sales.models import Customer, Order, OrderItem
from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
# ==========================================================
# Customers
# ==========================================================

class CustomerListView(ListView):
    model = Customer
    template_name = "sales/customer_list.html"
    context_object_name = "customers"

    def get_queryset(self):

        customers = (
            Customer.objects
            .annotate(
                total_orders=Count("orders"),
                total_amount=Coalesce(
                    Sum("orders__total"),
                    Decimal("0.00"),
                    output_field=DecimalField()
                )
            )
        )

        for customer in customers:

            transactions = Transaction.objects.filter(
                party_type="customer",
                party_id=customer.id
            )

            total_paid = (
                PaymentRecord.objects.filter(
                    transaction__in=transactions
                ).aggregate(
                    total=Sum("paid_amount")
                )["total"]
                or Decimal("0.00")
            )

            customer.total_paid = total_paid
            customer.balance = customer.total_amount - total_paid

        return customers


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "sales/customer_form.html"
    success_url = reverse_lazy("sales:customer_list")




class CustomerUpdateView(UpdateView):

    model = Customer
    form_class = CustomerForm
    template_name = "sales/customer_form.html"
    success_url = reverse_lazy("sales:customer_list")

    def form_valid(self, form):

        messages.success(
            self.request,
            "Customer updated successfully."
        )

        return super().form_valid(form)


class CustomerDeleteView(View):

    def post(self, request, pk):

        customer = get_object_or_404(
            Customer,
            pk=pk
        )

        if customer.orders.exists():

            messages.error(
                request,
                "This customer cannot be deleted because they have sales orders."
            )

            return redirect(
                "sales:customer_list"
            )

        customer.delete()

        messages.success(
            request,
            "Customer deleted successfully."
        )

        return redirect(
            "sales:customer_list"
        )





class CustomerDetailView(DetailView):
    model = Customer
    template_name = "sales/customer_detail.html"
    context_object_name = "customer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        customer = self.object

        orders = customer.orders.order_by("-created_at")

        transactions = (
            Transaction.objects
            .filter(
                party_type="customer",
                party_id=customer.id
            )
            .order_by("-created_at")
        )

        total_orders = orders.count()

        total_amount = (
            orders.aggregate(
                total=Coalesce(
                    Sum("total"),
                    Decimal("0.00"),
                    output_field=DecimalField()
                )
            )["total"]
        )

        total_paid = (
            PaymentRecord.objects.filter(
                transaction__in=transactions
            ).aggregate(
                total=Sum("paid_amount")
            )["total"]
            or Decimal("0.00")
        )

        remaining = total_amount - total_paid

        context.update({
            "orders": orders,
            "transactions": transactions,
            "total_orders": total_orders,
            "total_amount": total_amount,
            "total_paid": total_paid,
            "remaining": remaining,
        })

        return context


# ==========================================================
# Orders
# ==========================================================

class OrderListView(ListView):
    model = Order
    template_name = "sales/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):

        queryset = (
            Order.objects
            .select_related("customer")
            .annotate(
                item_count=Count("items")
            )
            .order_by("-created_at")
        )

        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(
                Q(customer__name__icontains=search)
                | Q(order_type__icontains=search)
                | Q(status__icontains=search)
                | Q(id__icontains=search)
            )

        return queryset


class OrderDetailView(DetailView):
    model = Order
    template_name = "sales/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return (
            Order.objects
            .select_related("customer")
            .prefetch_related(
                "items",
                "items__product_variant",
                "items__product_variant__product"
            )
        )

def order_create(request):

    if request.method == "POST":

        form = OrderForm(request.POST)

        if form.is_valid():

            variant_ids = request.POST.getlist("variant_id[]")
            qtys = request.POST.getlist("qty[]")
            prices = request.POST.getlist("price[]")

            if not (variant_ids and qtys and prices):
                messages.error(request, "Please add at least one item.")
                return render(request, "sales/order_form.html", {"form": form})

            try:
                with transaction.atomic():

                    order = form.save(commit=False)
                    order.status = "pending"
                    order.total = Decimal("0.00")
                    order.save()

                    grand_total = Decimal("0.00")

                    for variant_id, qty, price in zip(variant_ids, qtys, prices):

                        if not variant_id:
                            continue

                        qty = int(qty)
                        price = Decimal(str(price).replace(",", "").strip())

                        variant = ProductVariant.objects.select_for_update().get(pk=variant_id)

                        available_stock = variant.stock

                        if qty <= 0:
                            raise ValueError(f"{variant.sku}: Invalid quantity")

                        if qty > available_stock:
                            raise ValueError(
                                f"{variant.sku}: Only {available_stock} left in stock."
                            )

                        # ORDER ITEM
                        line_total = qty * price

                        OrderItem.objects.create(
                            order=order,
                            product_variant=variant,
                            qty=qty,
                            unit_price=price,
                            total=line_total
                        )

                        grand_total += line_total

                        # STOCK MOVEMENT (ONLY LOG, NO MANUAL UPDATE)
                        StockMovement.objects.create(
                            product_variant=variant,
                            type="STOCK_OUT",
                            qty=qty,
                            notes=f"Order #{order.id}"
                        )

                    order.total = grand_total
                    order.save(update_fields=["total"])

                    Transaction.objects.create(
                        type="incoming",
                        party_type="customer",
                        party_id=order.customer_id,
                        reference_type="customer_order",
                        reference_id=order.id,
                        amount=order.total,
                        status="pending",
                        notes=order.notes
                    )

                messages.success(request, "Order created successfully.")
                return redirect("sales:order_list")

            except Exception as e:
                messages.error(request, str(e))

        else:
            messages.error(request, "Form is invalid.")
            print(form.errors)

    else:
        form = OrderForm()

    return render(request, "sales/order_form.html", {"form": form})

# ==========================================================
# Ajax Search
# ==========================================================

def customer_search(request):

    term = request.GET.get("term", "")

    customers = Customer.objects.filter(
        name__icontains=term
    )[:20]

    results = [
        {
            "id": customer.id,
            "text": f"{customer.id} - {customer.name}"
        }
        for customer in customers
    ]

    return JsonResponse(
        {
            "results": results
        }
    )


def variant_search(request):

    term = request.GET.get("term", "")

    variants = (
        ProductVariant.objects
        .select_related(
            "product",
            "factory"
        )
        .filter(
            Q(sku__icontains=term)
            | Q(product__name__icontains=term)
            | Q(size__icontains=term)
            | Q(color__icontains=term)
            | Q(source_type__icontains=term)
        )[:20]
    )

    results = []

    for variant in variants:

        results.append({

            "id": variant.id,

            "text":
                f"{variant.sku} | "
                f"{variant.product.name} | "
                f"{variant.size or ''} | "
                f"{variant.color or ''}",

            "sku": variant.sku,
            "product": variant.product.name,
            "size": variant.size or "",
            "color": variant.color or "",
            "factory": variant.factory.name if variant.factory else "",
            "stock": variant.stock,
            "price": str(variant.selling_price)

        })

    return JsonResponse({
        "results": results
    })


@require_POST
def order_delete(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk
    )

    # Delete the accounting transaction
    Transaction.objects.filter(
        reference_id=order.id,
        party_type="customer"
    ).delete()

    # Deletes all OrderItems automatically
    order.delete()

    messages.success(
        request,
        "Order deleted successfully."
    )

    return redirect("sales:order_list")
