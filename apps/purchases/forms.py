from django import forms

from .models import Factory


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