from django.shortcuts import render, redirect
from django.contrib.auth import  logout

def contact_us(request):
    return render(request, "contact_us.html")

