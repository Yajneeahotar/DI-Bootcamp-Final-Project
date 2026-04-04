from django.db import models

#---Table for the list of properties---#
class Properties(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField()
    owner = models.CharField(max_length=200)
