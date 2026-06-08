from django import forms
from .models import Category

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