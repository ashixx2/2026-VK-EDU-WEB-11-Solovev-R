from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, ProfileForm, SignupForm


def get_safe_next_url(request, default_url_name="questions:index"):
    next_url = request.POST.get("next") or request.GET.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return reverse(default_url_name)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("questions:index")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect(get_safe_next_url(request))

    return render(request, "core/login.html", {
        "form": form,
        "next": request.POST.get("next") or request.GET.get("next", ""),
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect("questions:index")

    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("questions:index")

    return render(request, "core/signup.html", {
        "form": form,
    })


def logout_view(request):
    next_url = request.META.get("HTTP_REFERER")

    if not next_url or not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse("questions:index")

    logout(request)
    return redirect(next_url)


@login_required(login_url="core:login")
def profile(request):
    form = ProfileForm(request.POST or None, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("core:profile")

    return render(request, "core/profile.html", {
        "form": form,
    })