from django.urls import path
from . import views

urlpatterns = [
    path('contact_us/', views.contact_us, name='contactus'),
    path('property/<str:property_ref>/', views.property_contact, name='property_contact'),
]