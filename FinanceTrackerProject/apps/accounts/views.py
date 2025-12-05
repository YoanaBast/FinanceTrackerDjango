from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        errors = {}
        if password1 != password2:
            errors["__all__"] = ["Passwords do not match"]

        if User.objects.filter(username=username).exists():
            errors.setdefault("__all__", []).append("Username already taken")

        if User.objects.filter(email=email).exists():
            errors.setdefault("__all__", []).append("Email already taken")

        if errors:
            return render(request, "accounts/register.html", {"form": {"errors": errors}})

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect("dashboard")  # replace with your landing page

    return render(request, "accounts/register.html", {"form": {}})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")  # change to your dashboard

        return render(request, "accounts/login.html", {
            "form": {"errors": {"__all__": ["Invalid username or password"]}}
        })

    return render(request, "accounts/login.html", {"form": {}})


def logout_view(request):
    logout(request)
    return redirect("dashboard")  # redirect to landing page or login page