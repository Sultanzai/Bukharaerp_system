from django import forms
from apps.sales.models import Customer


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = [
            'name',
            'phone',
            'email',
            'address',
            'active'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }