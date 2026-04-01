from django.shortcuts import render
from .models import Properties
	
#---retrieve all records properties table ---#
# --- Store in listings and send to HTML ---#
def property_listings(request):
    listings = Properties.objects.all().order_by("-id")
    return render(request, "properties.html", {"properties_list": listings})