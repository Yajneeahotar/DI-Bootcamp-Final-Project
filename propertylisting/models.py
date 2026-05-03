from django.db import models, transaction
from cloudinary.models import CloudinaryField
from django.conf import settings

#---Table for the list of properties---#
class Properties(models.Model):
    property_ref = models.CharField(
        max_length=10,
        primary_key=True,
        editable=False,
        #verbose_name="Property Ref. No."
    )
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField()
    rooms = models.PositiveIntegerField(default=0, blank=True)
    bedrooms = models.PositiveIntegerField(default=0, blank=True)
    area = models.PositiveIntegerField(default=0, blank=True)
    image = CloudinaryField('image')
    owner = models.CharField(max_length=200)
   # type = models.CharField(max_length=200)


    #use custom save method to generate property_ref in the format YK0001, YK0002, etc. when a new property is created
    def save(self, *args, **kwargs):
        if not self.property_ref:
            # Below code ensures that even if multiple users are creating properties at the same time, each property will get a unique property_ref without conflicts. It does this by using a database transaction and locking the relevant rows until the new property_ref is generated and saved.
            # wraps the read+write in a single atomic database transaction. If anything fails, it rolls back completely.
            with transaction.atomic():
                # place a database-level lock on the selected row (select for update)
                last = Properties.objects.select_for_update().order_by('property_ref').last()
                if last:
                    last_num = int(last.property_ref[2:])  # Strip 'YK(2)', get number
                    new_num = last_num + 1
                else:
                    new_num = 1
                self.property_ref = f'YK{new_num:04d}'
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
    
#---Table for user favorites---#
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Properties, on_delete=models.CASCADE, related_name='favorited_by')
                
    class Meta:
        unique_together = ('user', 'property')