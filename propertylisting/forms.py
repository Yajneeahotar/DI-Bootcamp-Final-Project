from django import forms
from .models import Properties, PropertyEditRequest

class PropertiesForm(forms.ModelForm):
    class Meta:
        model = Properties
        fields = [
            "title",
            "location",
            "price",
            "description",
            "rooms",
            "bedrooms",
            "area",
            "image",
        ]

class PropertyEditForm(forms.ModelForm):
    class Meta:
        model = PropertyEditRequest
        fields = [
            "title",
            "location",
            "price",
            "description",
            "rooms",
            "bedrooms",
            "area",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False