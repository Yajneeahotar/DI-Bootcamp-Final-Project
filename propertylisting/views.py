from django.shortcuts import render, redirect
from .models import Properties
from .forms import PropertiesForm
	
#---retrieve all records properties table ---#
# --- Store in listings and send to HTML ---#
def property_listings(request):
    listings = Properties.objects.all().order_by("-id")
    return render(request, "properties.html", {"properties_list": listings})

def properties(request):
    return render(request, "properties.html")

def create_property(request):
    if request.method == "POST":
        form = PropertiesForm(request.POST, request.FILES) #This handles text data from form and images
        if form.is_valid():
            form.save()
            return redirect('properties')
    else:
        form = PropertiesForm()

    return render(request, 'create.html', {'form': form})