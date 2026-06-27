# apps/accounting/forms.py

from decimal import Decimal

from django import forms

from .models import HawalaAccount, HawalaTransaction, PaymentRecord


class PaymentRecordForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.remaining_amount = kwargs.pop('remaining_amount', None)
        super().__init__(*args, **kwargs)

    payment_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = PaymentRecord
        fields = [
            'paid_amount',
            'currency_rate',
            'payment_method',
            'code_number',
            'payment_date',
            'notes'
        ]

        widgets = {
            'paid_amount': forms.NumberInput(attrs={
                'class': 'form-control'
            }),

            'currency_rate': forms.NumberInput(attrs={
                'class': 'form-control'
            }),

            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),

            'code_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def clean_paid_amount(self):

        paid_amount = self.cleaned_data['paid_amount']

        if paid_amount <= Decimal('0'):
            raise forms.ValidationError(
                'Payment amount must be greater than zero.'
            )

        if self.remaining_amount is not None:
            if paid_amount > self.remaining_amount:
                raise forms.ValidationError(
                    f'Payment amount cannot exceed remaining amount ({self.remaining_amount}).'
                )

        return paid_amount
    


class HawalaAccountForm(forms.ModelForm):

    class Meta:
        model = HawalaAccount

        fields = [
            'name',
            'contact_person',
            'phone',
            'email',
            'city',
            'address',
            'notes',
            'is_active'
        ]

        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'contact_person': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),

            'city': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),

            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })

        }


class HawalaTransactionForm(forms.ModelForm):

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

            "debit",

            "credit",

            "currency_rate",

            "payment_method",

            "reference_type",

            "reference_id",

            "reference_number",

            "transaction_date",

            "status",

            "notes",

        ]

        widgets = {

            "transaction_type": forms.Select(attrs={
                "class": "form-select"
            }),

            "debit": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "credit": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "currency_rate": forms.NumberInput(attrs={
                "class": "form-control"
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

        cleaned = super().clean()

        debit = cleaned.get("debit") or 0

        credit = cleaned.get("credit") or 0

        if debit == 0 and credit == 0:

            raise forms.ValidationError(
                "Enter either Debit or Credit."
            )

        if debit > 0 and credit > 0:

            raise forms.ValidationError(
                "Only one of Debit or Credit can have a value."
            )

        return cleaned