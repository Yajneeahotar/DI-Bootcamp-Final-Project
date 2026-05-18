from django.contrib import admin
from .models import Properties, Favorite, PropertyImage, Notification

admin.site.register(Properties)
admin.site.register(Favorite)
admin.site.register(PropertyImage)
admin.site.register(Notification)
