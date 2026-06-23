# apps/accounting/forms.py

from decimal import Decimal

from django import forms

from .models import PaymentRecord


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