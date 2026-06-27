# apps/investors/forms.py

from django import forms
from .models import Investor
from decimal import Decimal
from .models import InvestorTransaction



class InvestorForm(forms.ModelForm):

    class Meta:
        model = Investor

        fields = [
            'name',
            'phone',
            'email',
            'address',
            'notes',
            'is_active'
        ]

        widgets = {

            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'email': forms.EmailInput(attrs={
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






class InvestorTransactionForm(forms.ModelForm):

    transaction_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = InvestorTransaction

        fields = [
            'type',
            'amount',
            'currency_rate',
            'payment_method',
            'reference_number',
            'transaction_date',
            'status',
            'notes'
        ]

        widgets = {

            'type': forms.Select(attrs={
                'class': 'form-select'
            }),

            'amount': forms.NumberInput(attrs={
                'class': 'form-control'
            }),

            'currency_rate': forms.NumberInput(attrs={
                'class': 'form-control'
            }),

            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),

            'reference_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'status': forms.Select(attrs={
                'class': 'form-select'
            }),

            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })

        }

    def __init__(self, *args, **kwargs):

        self.current_balance = kwargs.pop(
            'current_balance',
            Decimal('0')
        )

        super().__init__(*args, **kwargs)

    def clean(self):

        cleaned_data = super().clean()

        transaction_type = cleaned_data.get('type')

        amount = cleaned_data.get('amount')

        if amount and amount <= 0:

            raise forms.ValidationError(
                'Amount must be greater than zero.'
            )

        if (
            transaction_type == 'withdrawal'
            and amount
            and amount > self.current_balance
        ):

            raise forms.ValidationError(
                f'Withdrawal amount cannot exceed balance ({self.current_balance}).'
            )

        return cleaned_data