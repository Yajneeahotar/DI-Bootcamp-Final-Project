from django.db import models
from cloudinary.models import CloudinaryField

#---Table for the list of properties---#
class Properties(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField()
    rooms = models.PositiveIntegerField(default=0, blank=True)
    bedrooms = models.PositiveIntegerField(default=0, blank=True)
    area = models.PositiveIntegerField(default=0, blank=True)
    #image = models.ImageField()
    image = CloudinaryField('image')
    owner = models.CharField(max_length=200)
