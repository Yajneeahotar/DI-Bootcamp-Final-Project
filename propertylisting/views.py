from django.shortcuts import render, redirect, get_object_or_404
from .models import Properties, Favorite
from .forms import PropertiesForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
	
#---retrieve all records properties table ---#
# --- Store in listings and send to HTML ---#
def property_listings(request):
    listings = Properties.objects.all().order_by("-id")
    return render(request, "properties.html", {"properties_list": listings})#---retrieve all records properties table ---#
# --- Store in listings and send to HTML ---#
def property_listings(request):
    listings = Properties.objects.all().order_by("-id")
    favorited_ids = set()
    if request.user.is_authenticated:
        favorited_ids = set(
            Favorite.objects.filter(user=request.user).values_list('property_id', flat=True)
        )
    return render(request, "properties.html", {
        "properties_list": listings,
        "favorited_ids": favorited_ids,
    })

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

#further propety information while clicking on property cards
def property_info(request, id):
    property = get_object_or_404(Properties, id=id)
    return render(request, 'propertyinfo.html', {'property': property})

@require_POST
@login_required
def toggle_favorite(request, id):
    property_obj = get_object_or_404(Properties, id=id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
    if not created:
        favorite.delete()
    return redirect('properties')