from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    property = models.ForeignKey(
        'propertylisting.Properties',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='contact_messages',
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email}) — {self.submitted_at:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

