from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm


def login_view(request):

    if request.user.is_authenticated:
        return redirect("core:dashboard")

    form = LoginForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            user = form.user

            login(request, user)

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            messages.success(
                request,
                f"Welcome back, {user.get_full_name() or user.username}."
            )

            return redirect("core:dashboard")

    return render(
        request,
        "users/login.html",
        {
            "form": form,
        }
    )


@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("users:login")


@login_required
def profile_view(request):

    return render(
        request,
        "users/profile.html"
    )