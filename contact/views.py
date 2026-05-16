from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            subject = f"New Contact Form Message from {contact_message.name}"
            body = (
                f"Name: {contact_message.name}\n"
                f"Email: {contact_message.email}\n"
                f"Phone: {contact_message.phone or 'N/A'}\n\n"
                f"Message:\n{contact_message.message}"
            )
            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                return render(request, 'contact_us.html', {'form': ContactForm(), 'success': True})
            except Exception:
                return render(request, 'contact_us.html', {'form': form, 'error': True})
        # Form is invalid — re-render with errors
        return render(request, 'contact_us.html', {'form': form})
    else:
        form = ContactForm()
    return render(request, 'contact_us.html', {'form': form})

