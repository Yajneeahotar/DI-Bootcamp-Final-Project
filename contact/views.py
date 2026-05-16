from django.shortcuts import render, redirect, get_object_or_404
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

def property_contact(request, property_ref):
    if request.method != 'POST':
        return redirect('property_info', property_ref=property_ref)

    from propertylisting.models import Properties
    property_obj = get_object_or_404(Properties, property_ref=property_ref)
    form = ContactForm(request.POST)
    if form.is_valid():
        contact_message = form.save(commit=False)
        contact_message.property = property_obj
        contact_message.save()
        subject = f"Property Enquiry — Ref: {property_obj.property_ref} from {contact_message.name}"
        body = (
            f"Property Ref: {property_obj.property_ref}\n"
            f"Property Title: {property_obj.title}\n\n"
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
            return redirect(f"/properties/info/{property_ref}/?contact=success")
        except Exception:
            return redirect(f"/properties/info/{property_ref}/?contact=error")
    return redirect(f"/properties/info/{property_ref}/?contact=error")
