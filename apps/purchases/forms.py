from django import forms
from django.forms import inlineformset_factory
from .models import PurchaseOrder, PurchaseOrderItem
from .models import (
    Factory,
    PurchaseOrder,
    PurchaseOrderItem
)


class FactoryForm(forms.ModelForm):

    class Meta:

        model = Factory

        fields = [
            "name",
            "phone",
            "email",
            "gstin",
            "supliercode",
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

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "gstin": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "supliercode": forms.TextInput(
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
            "transport_tax_expenses_cost",
            "notes",
        ]

        labels = {

            "po_number": "PO Number",

            "order_date": "Order Date",

            "expected_date": "Expected Date",

            "status": "Status",

            "transport_tax_expenses_cost": "Transport / Tax Expense",

            "notes": "Notes",
        }

        widgets = {

            "po_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "PO Number"
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

            "transport_tax_expenses_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Transport / Tax Expense"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Notes"
                }
            ),
        }


class PurchaseOrderItemForm(forms.ModelForm):

    class Meta:

        model = PurchaseOrderItem

        fields = [
            "product_code",
            "product_name",
            "quantity",
            "price"
        ]

        labels = {

            "product_code": "Product Code",

            "product_name": "Product Name",

            "quantity": "Quantity",

            "price": "Price"
        }

        widgets = {

            "product_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Product Code"
                }
            ),

            "product_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Product Name"
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control qty",
                    "placeholder": "Qty"
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control price",
                    "step": "0.01",
                    "placeholder": "Price"
                }
            )
        }
        
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True
)