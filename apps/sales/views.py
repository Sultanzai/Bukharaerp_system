from decimal import Decimal

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView

from apps.products.models import Product
from apps.sales.forms import CustomerForm, OrderForm
from apps.sales.models import Customer, Order, OrderItem
from django.http import JsonResponse
from apps.products.models import ProductVariant
from django.http import JsonResponse
from django.db.models import Q, Count
from apps.products.models import ProductVariant

# ==========================
# Customers
# ==========================

class CustomerListView(ListView):
    model = Customer
    template_name = "sales/customer_list.html"
    context_object_name = "customers"


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "sales/customer_form.html"
    success_url = reverse_lazy("sales:customer_list")


# ==========================
# Orders
# ==========================

class OrderListView(ListView):
    model = Order
    template_name = "sales/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):

        queryset = (
            Order.objects
            .select_related("customer")
            .annotate(item_count=Count("items"))
            .order_by("-created_at")
        )

        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(
                Q(customer__name__icontains=search) |
                Q(order_type__icontains=search) |
                Q(status__icontains=search) |
                Q(id__icontains=search)
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

            # SYSTEM CONTROLLED STATUS
            order.status = "pending"
            order.total = Decimal("0.00")
            order.save()

            variant_ids = request.POST.getlist("variant_id[]")
            qtys = request.POST.getlist("qty[]")
            prices = request.POST.getlist("price[]")

            grand_total = Decimal("0.00")

            if not (variant_ids and qtys and prices):
                messages.error(request, "Order items are missing.")
                return render(request, "sales/order_form.html", {"form": form})

            for variant_id, qty, price in zip(variant_ids, qtys, prices):

                try:
                    if not variant_id or not qty or not price:
                        continue

                    qty = int(qty)
                    price = Decimal(str(price).replace(",", "").strip())

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
                    messages.error(request, f"Item error: {str(e)}")
                    return render(request, "sales/order_form.html", {"form": form})

            # FINAL UPDATE (ONLY ONCE)
            order.total = grand_total
            order.save(update_fields=["total"])

            messages.success(request, "Order created successfully.")
            return redirect("sales:order_list")

        else:
            print(form.errors)
            messages.error(request, "Form is invalid.")

    else:
        form = OrderForm()

    return render(request, "sales/order_form.html", {"form": form})


def customer_search(request):

    term = request.GET.get("term", "")

    customers = Customer.objects.filter(
        name__icontains=term
    )[:20]

    results = []

    for customer in customers:

        results.append({
            "id": customer.id,
            "text": f"{customer.id} - {customer.name}"
        })

    return JsonResponse({
        "results": results
    })


from django.http import JsonResponse
from django.db.models import Q
from apps.products.models import ProductVariant


def variant_search(request):

    term = request.GET.get("term", "")

    variants = (
        ProductVariant.objects
        .select_related("product", "factory")
        .filter(
            Q(sku__icontains=term) |
            Q(product__name__icontains=term) |
            Q(size__icontains=term) |
            Q(color__icontains=term) |
            Q(source_type__icontains=term)
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

    return JsonResponse({
        "results": results
    })