from django.shortcuts import render, redirect, get_object_or_404
from .models import Properties, Favorite
from .forms import PropertiesForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
'''def property_listings(request):
    listings = Properties.objects.all().order_by("-id")
    return render(request, "properties.html", {"properties_list": listings})#---retrieve all records properties table ---#'''

#---retrieve all records properties table ---#
# --- Store in listings and send to HTML ---#
def property_listings(request):
    listings = Properties.objects.all().order_by("-property_ref")
    favorited_ids = set()
    favorites_count = 0

    if request.user.is_authenticated:
        # Get IDs of properties, from favorite table, favorited by the current user
        # purpose is to check/unchecked the favorite icon in each card in properties.html page
        favorited_ids = set(
            Favorite.objects.filter(user=request.user).values_list('property__property_ref', flat=True)
        )
        # purpose is to show the number of favorited properties in the favorite icon in navbar in properties.html page
        favorites_count = len(favorited_ids)

    return render(request, "properties.html", {
        "properties_list": listings,
        "favorited_ids": favorited_ids,
        "favorites_count": favorites_count,
    })

#--used for favorite icon (navbar) to show only favorited properties for current user in properties.html page--#
@login_required
def favorites_list(request):
    # Get IDs of properties, from favorite table, favorited by the current user
    favorited_ids = set(
        Favorite.objects.filter(user=request.user).values_list('property__property_ref', flat=True)
    )

    listings = Properties.objects.filter(property_ref__in=favorited_ids).order_by("-property_ref")

    return render(request, "properties.html", {"properties_list": listings,           # parameter related to cards
                                               "favorited_ids": favorited_ids,        # parameter related to favorite icon in each card (filled or unfilled)
                                               "favorites_count": len(favorited_ids), # parameter related to favorite icon in navbar (number of favorited properties)
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
def property_info(request, property_ref):
    property = get_object_or_404(Properties, property_ref=property_ref)
    return render(request, 'propertyinfo.html', {'property': property})

@require_POST
@login_required
def toggle_favorite(request, property_ref):
    property_obj = get_object_or_404(Properties, property_ref=property_ref)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
    if not created:
        favorite.delete()
    return redirect('properties')

#this view is for the sell property button in navbar
def sell_property(request):
    if request.user.is_authenticated:
        return redirect('create_property')
    return render(request, 'sell_landing.html')