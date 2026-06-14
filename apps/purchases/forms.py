from django import forms

from .models import (
    Factory,
    PurchaseOrder
)


class FactoryForm(forms.ModelForm):

    class Meta:

        model = Factory

        fields = [
            "name",
            "phone",
            "address",
            "notes",
            "status",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "status": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            )
        }


class PurchaseOrderForm(forms.ModelForm):

    class Meta:

        model = PurchaseOrder

        fields = [
            "po_number",
            "order_date",
            "expected_date",
            "status",
            "subtotal",
            "transport_tax_expenses_cost",
            "total",
            "notes",
        ]

        widgets = {

            "po_number": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "order_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "expected_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "subtotal": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),

            "transport_tax_expenses_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),

            "total": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),
        }