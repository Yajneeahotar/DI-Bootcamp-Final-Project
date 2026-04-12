from django.urls import path
from . import views

urlpatterns = [
    path('properties_list/', views.property_listings, name='properties'),
    path('add/', views.create_property, name='create_property'),
]