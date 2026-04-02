from django.db import models

#---Table for the list of properties---#
class Properties(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price_per_month = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    image = models.ImageField()
    owner = models.CharField(max_length=200)
