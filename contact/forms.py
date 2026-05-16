from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'name',
                'placeholder': 'Your Name',
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'id': 'email',
                'placeholder': 'Your Email',
                'class': 'form-control',
            }),
            'phone': forms.TextInput(attrs={
                'id': 'phone',
                'placeholder': 'Your Phone Number',
                'class': 'form-control',
                'type': 'tel',
            }),
            'message': forms.Textarea(attrs={
                'id': 'message',
                'placeholder': 'Your Message',
                'rows': 5,
                'class': 'form-control',
            }),
        }
