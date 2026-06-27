from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Sum, Q, DecimalField
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from apps.accounting.models import Transaction, PaymentRecord
from apps.products.models import ProductVariant
from apps.sales.forms import CustomerForm, OrderForm
from apps.sales.models import Customer, Order, OrderItem


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

            order = form.save(commit=False)
            order.status = "pending"
            order.total = Decimal("0.00")
            order.save()

            variant_ids = request.POST.getlist("variant_id[]")
            qtys = request.POST.getlist("qty[]")
            prices = request.POST.getlist("price[]")

            grand_total = Decimal("0.00")

            if not (variant_ids and qtys and prices):
                messages.error(request, "Order items are missing.")
                return render(
                    request,
                    "sales/order_form.html",
                    {"form": form}
                )

            for variant_id, qty, price in zip(
                    variant_ids,
                    qtys,
                    prices):

                try:

                    if not variant_id or not qty or not price:
                        continue

                    qty = int(qty)

                    price = Decimal(
                        str(price).replace(",", "").strip()
                    )

                    if qty <= 0 or price <= 0:
                        continue

                    line_total = Decimal(qty) * price

                    OrderItem.objects.create(
                        order=order,
                        product_variant_id=int(variant_id),
                        qty=qty,
                        unit_price=price,
                        total=line_total
                    )

                    grand_total += line_total

                except Exception as e:

                    messages.error(
                        request,
                        f"Item error: {str(e)}"
                    )

                    return render(
                        request,
                        "sales/order_form.html",
                        {"form": form}
                    )

            order.total = grand_total

            order.save(
                update_fields=["total"]
            )

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

            messages.success(
                request,
                "Order created successfully."
            )

            return redirect(
                "sales:order_list"
            )

        else:

            print(form.errors)

            messages.error(
                request,
                "Form is invalid."
            )

    else:

        form = OrderForm()

    return render(
        request,
        "sales/order_form.html",
        {
            "form": form
        }
    )


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
            "stock": getattr(variant, "quantity", 0),
            "price": str(variant.selling_price)

        })

    return JsonResponse(
        {
            "results": results
        }
    )