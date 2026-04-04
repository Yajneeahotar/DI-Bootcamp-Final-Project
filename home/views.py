from django.shortcuts import render

def homepage(request):
    return render(request, "home/home.html")

def search_filter(request):
    print(request)
    return render(request, "properties.html")
    

