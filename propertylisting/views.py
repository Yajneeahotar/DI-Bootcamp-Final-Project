from django.shortcuts import render, redirect
from .models import Properties
from .forms import PropertiesForm
from django.contrib.auth.decorators import login_required
	
#---retrieve all records properties table ---#
# --- Store in listings and send to HTML ---#
def property_listings(request):
    listings = Properties.objects.all().order_by("-id")
    return render(request, "properties.html", {"properties_list": listings})

def properties(request):
    return render(request, "properties.html")

@login_required
def create_property(request):
    if request.method == "POST":
        form = PropertiesForm(request.POST, request.FILES)
        if form.is_valid():
            property_record= form.save(commit=False)
            property_record.owner = request.user.username
            property_record.save()
            return redirect('properties')
    else:
        form = PropertiesForm()

    return render(request, 'create.html', {'form': form})

def details(request):
    return render(request, "details.html")