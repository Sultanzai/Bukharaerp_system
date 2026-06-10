from django import forms
from .models import Category
from .models import ProductVariant
from .models import Product

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category

        fields = [
            "name",
            "type",
            "description"
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "type": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),
        }






class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            "category",
            "name",
            "active",
        ]

        widgets = {

            "category": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

        }








class ProductVariantForm(forms.ModelForm):

    opening_stock = forms.IntegerField(
        min_value=0,
        initial=0,
        required=False
    )

    class Meta:

        model = ProductVariant

        fields = [

            "sku",

            "size",

            "color",

            "source_type",

            "factory",

            "cost_price",

            "selling_price"

        ]

        widgets = {

            "sku": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "size": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "color": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "source_type": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "factory": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "cost_price": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "selling_price": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "opening_stock": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

        }