from django.urls import path
from . import views

urlpatterns = [
    path('properties_list/', views.property_listings, name='properties'),
    path('favorites/', views.favorites_list, name='my_favorites'),
    path('add/', views.create_property, name='create_property'),
    path('details/', views.details, name='details'),
    path('info/<str:property_ref>/', views.property_info, name='property_info'),
    path('favorite/<str:property_ref>/', views.toggle_favorite, name='toggle_favorite'),
]