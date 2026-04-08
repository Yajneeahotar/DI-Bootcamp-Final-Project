from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm

def login(request):
    return render(request, "login.html")

def register_view(request):
    if request.user.is_authenticated:
       return redirect("homepage")  

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            print("USER CREATED")  
        else:
            print(form.errors)  

            
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Account created for {username}! You can now log in."
            )
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})
