from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.user.is_authenticated:
        return redirect("homepage")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect("homepage")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html", {})

def register_view(request):
    if request.user.is_authenticated:
       return redirect("homepage")  

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
           
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Account created for {username}! You can now log in."
            )
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})
