from django.views.generic import ListView, TemplateView
from django.shortcuts import redirect
from .models import Category, ProductVariant, StockMovement
from .forms import CategoryForm
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Prefetch, Sum
from django.db.models.functions import Coalesce 

from apps.products.models import Product
from .forms import ProductForm, ProductVariantForm


class ProductHomeView(TemplateView):

    template_name = "products/index.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["products"] = Product.objects.select_related(
            "category"
        ).prefetch_related(
            "variants"
        ).order_by(
            "-id"
        )

        return context

class MasterProductView(TemplateView):

    template_name = "products/product_form.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["form"] = ProductForm()

        context["products"] = Product.objects.select_related(
            "category"
        ).order_by("-id")

        return context

    def post(self, request, *args, **kwargs):

        form = ProductForm(request.POST)

        if form.is_valid():

            product = form.save()

            return redirect(
                "products:variants",
                product_id=product.id
            )

        context = {
            "form": form,
            "products": Product.objects.select_related(
                "category"
            ).order_by("-id")
        }

        return self.render_to_response(context)
    

class CategoryView(TemplateView):

    template_name = "products/categories.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["form"] = CategoryForm()

        context["categories"] = Category.objects.all()

        return context

    def post(self, request, *args, **kwargs):

        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()

        return redirect("products:products-home")
    
    
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm

    template_name = "products/product_form.html"

    success_url = "/products/"


class ProductListView(ListView):
    model = Product

    template_name = "products/index.html"

    context_object_name = "products"

    queryset = Product.objects.select_related(
        "category"
    ).order_by("name")






class ProductVariantView(TemplateView):

    template_name = "products/variants.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        product = get_object_or_404(
            Product,
            pk=self.kwargs["product_id"]
        )

        context["product"] = product

        context["form"] = ProductVariantForm()

        context["variants"] = product.variants.all()

        return context

    def post(self, request, *args, **kwargs):

        product = get_object_or_404(
            Product,
            pk=self.kwargs["product_id"]
        )

        form = ProductVariantForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                variant = form.save(
                    commit=False
                )

                variant.product = product

                variant.save()

                opening_stock = form.cleaned_data[
                    "opening_stock"
                ]

                if opening_stock > 0:

                    StockMovement.objects.create(

                        product_variant=variant,

                        type="OPENING",

                        qty=opening_stock,

                        # related_docs="MASTER_PRODUCT",

                        # file_number=product.id,

                        notes="Opening Stock"

                    )

            return redirect(
                "products:variants",
                product_id=product.id
            )

        return self.render_to_response({

            "product": product,

            "form": form,

            "variants": product.variants.all()

        })
    




class StockMovementView(TemplateView):

    template_name = "products/stock_movement.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        products = Product.objects.prefetch_related(

            Prefetch(

                "variants",

                queryset=ProductVariant.objects.annotate(

                    total_stock=Coalesce(
                        Sum("stock_movements__qty"),
                        0
                    )

                )

            )

        )

        context["products"] = products

        return context



class StockInView(TemplateView):

    template_name = "products/stock_in.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        product = get_object_or_404(
            Product,
            pk=self.kwargs["product_id"]
        )

        variants = ProductVariant.objects.filter(
            product=product
        )

        context["product"] = product
        context["variants"] = variants

        return context

    def post(self, request, *args, **kwargs):

        product = get_object_or_404(
            Product,
            pk=self.kwargs["product_id"]
        )

        variants = ProductVariant.objects.filter(
            product=product
        )

        for variant in variants:

            qty = request.POST.get(
                f"qty_{variant.id}"
            )

            notes = request.POST.get(
                f"notes_{variant.id}"
            )

            if qty and int(qty) > 0:

                StockMovement.objects.create(

                    product_variant=variant,

                    type="STOCK_IN",

                    qty=int(qty),

                    notes=notes

                )

        return redirect(
            "products:stock-movement"
        )



class ProductDetailView(TemplateView):

    template_name = "products/product_detail.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        product = get_object_or_404(
            Product,
            pk=self.kwargs["product_id"]
        )

        variants = ProductVariant.objects.filter(
            product=product
        ).select_related(
            "factory"
        ).annotate(
            total_stock=Coalesce(
                Sum("stock_movements__qty"),
                0
            )
        )

        stock_movements = StockMovement.objects.filter(
            product_variant__product=product
        ).select_related(
            "product_variant"
        ).order_by(
            "-created_at"
        )

        context["product"] = product
        context["variants"] = variants
        context["stock_movements"] = stock_movements

        return context