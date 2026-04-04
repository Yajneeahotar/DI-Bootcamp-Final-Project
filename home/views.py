from django.shortcuts import render
from propertylisting.models import Properties
from django.db.models import Q

def homepage(request):
    return render(request, "home/home.html")

def search_filter(request):
    listings = Properties.objects.all().order_by("-id")

    #request.GET == it is returning a dictionary
    #.get() == retrieving key value pairs. Eg: key = location, value = location value
    #<QueryDict: {'location': ['Bamboo'], 'min_price': [''], 'max_price': [''], 'keywords': ['']}> 
    location = request.GET.get("location") 
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    keywords = request.GET.get("keywords")
    
    if location:
        listings = listings.filter(location__icontains=location)  #If the user entered a location, return all listings whose location contains that text (ignoring uppercase/lowercase)

    if min_price:
        listings = listings.filter(price__gte=min_price) #gte - greater than or equal to
    
    if max_price:
        listings = listings.filter(price__lte=max_price) #lte - less than or equal to
    
    if keywords:
        listings = Properties.objects.filter(Q(title__icontains=keywords) | Q(description__icontains=keywords) | Q(location__icontains=keywords))
    return render(request, "properties.html", {"properties_list": listings})
    

