from django.views.generic import ListView, TemplateView
from django.shortcuts import redirect
from .models import Category
from .forms import CategoryForm

from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.products.models import Product
from apps.products.forms import ProductForm


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

            form.save()

            return redirect("products:master-products")

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