# apps/accounting/forms.py

from decimal import Decimal

from django import forms

from .models import (
    HawalaAccount,
    HawalaTransaction,
    PaymentRecord
)


# ==========================================================
# Payment Record
# ==========================================================

class PaymentRecordForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        self.remaining_amount = kwargs.pop(
            "remaining_amount",
            None
        )

        super().__init__(*args, **kwargs)

    payment_date = forms.DateField(

        widget=forms.DateInput(

            attrs={
                "type": "date",
                "class": "form-control"
            }

        )

    )

    class Meta:

        model = PaymentRecord

        fields = [

            "paid_amount",

            "currency_rate",

            "payment_method",

            "code_number",

            "payment_date",

            "notes"

        ]

        widgets = {

            "paid_amount": forms.NumberInput(attrs={

                "class": "form-control",

                "min": "0.01",

                "step": "0.01"

            }),

            "currency_rate": forms.NumberInput(attrs={

                "class": "form-control",

                "step": "0.0001"

            }),

            "payment_method": forms.Select(attrs={

                "class": "form-select"

            }),

            "code_number": forms.TextInput(attrs={

                "class": "form-control"

            }),

            "notes": forms.Textarea(attrs={

                "class": "form-control",

                "rows": 3

            }),

        }

    def clean_paid_amount(self):

        paid_amount = self.cleaned_data["paid_amount"]

        if paid_amount <= Decimal("0"):

            raise forms.ValidationError(

                "Payment amount must be greater than zero."

            )

        if self.remaining_amount is not None:

            if paid_amount > self.remaining_amount:

                raise forms.ValidationError(

                    f"Payment cannot exceed remaining amount ({self.remaining_amount})."

                )

        return paid_amount


# ==========================================================
# Hawala Account
# ==========================================================

class HawalaAccountForm(forms.ModelForm):

    class Meta:

        model = HawalaAccount

        fields = [

            "name",

            "contact_person",

            "phone",

            "email",

            "city",

            "address",

            "notes",

            "is_active"

        ]

        widgets = {

            "name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "contact_person": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),

            "city": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "address": forms.Textarea(attrs={

                "class": "form-control",

                "rows": 3

            }),

            "notes": forms.Textarea(attrs={

                "class": "form-control",

                "rows": 3

            }),

            "is_active": forms.CheckboxInput(attrs={

                "class": "form-check-input"

            })

        }


# ==========================================================
# Hawala Transaction
# ==========================================================

class HawalaTransactionForm(forms.ModelForm):

    credit = forms.DecimalField(

        label="Money Added (+)",

        required=False,

        min_value=0,

        decimal_places=2,

        max_digits=14,

        help_text="Money added to this Hawala account.",

        widget=forms.NumberInput(

            attrs={

                "class": "form-control",

                "placeholder": "0.00",

                "step": "0.01"

            }

        )

    )

    debit = forms.DecimalField(

        label="Money Removed (-)",

        required=False,

        min_value=0,

        decimal_places=2,

        max_digits=14,

        help_text="Money removed from this Hawala account.",

        widget=forms.NumberInput(

            attrs={

                "class": "form-control",

                "placeholder": "0.00",

                "step": "0.01"

            }

        )

    )

    transaction_date = forms.DateField(

        widget=forms.DateInput(

            attrs={

                "type": "date",

                "class": "form-control"

            }

        )

    )

    class Meta:

        model = HawalaTransaction

        fields = [

            "transaction_type",

            "credit",

            "debit",

            "currency_rate",

            "payment_method",

            "reference_type",

            "reference_id",

            "reference_number",

            "transaction_date",

            "status",

            "notes"

        ]

        widgets = {

            "transaction_type": forms.Select(attrs={

                "class": "form-select"

            }),

            "currency_rate": forms.NumberInput(attrs={

                "class": "form-control",

                "step": "0.0001"

            }),

            "payment_method": forms.Select(attrs={

                "class": "form-select"

            }),

            "reference_type": forms.TextInput(attrs={

                "class": "form-control"

            }),

            "reference_id": forms.NumberInput(attrs={

                "class": "form-control"

            }),

            "reference_number": forms.TextInput(attrs={

                "class": "form-control"

            }),

            "status": forms.Select(attrs={

                "class": "form-select"

            }),

            "notes": forms.Textarea(attrs={

                "class": "form-control",

                "rows": 3

            })

        }

    def clean(self):

        cleaned_data = super().clean()

        credit = cleaned_data.get("credit") or Decimal("0")

        debit = cleaned_data.get("debit") or Decimal("0")

        if credit < 0:

            self.add_error(

                "credit",

                "Money Added cannot be negative."

            )

        if debit < 0:

            self.add_error(

                "debit",

                "Money Removed cannot be negative."

            )

        if credit == 0 and debit == 0:

            raise forms.ValidationError(

                "Enter either Money Added or Money Removed."

            )

        if credit > 0 and debit > 0:

            raise forms.ValidationError(

                "A transaction cannot contain both Money Added and Money Removed."

            )

        return cleaned_data