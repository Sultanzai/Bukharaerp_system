from django.views.generic import ListView, TemplateView
from django.shortcuts import redirect
from .models import Category, StockMovement
from .forms import CategoryForm
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.products.models import Product
from .forms import ProductForm, ProductVariantForm



class ProductHomeView(TemplateView):

    template_name = "products/index.html"

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

        return redirect("products:categories")
    
    
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

                        movement_type="OPENING",

                        qty=opening_stock,

                        related_docs="MASTER_PRODUCT",

                        file_number=product.id,

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