from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):

    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter username",
                "autocomplete": "username",
            }
        )
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password",
                "autocomplete": "current-password",
            }
        )
    )

    def clean(self):

        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:

            self.user = authenticate(
                username=username,
                password=password
            )

            if self.user is None:

                raise forms.ValidationError(
                    "Invalid username or password."
                )

            if not self.user.is_active:

                raise forms.ValidationError(
                    "This account is inactive."
                )

        return cleaned_data