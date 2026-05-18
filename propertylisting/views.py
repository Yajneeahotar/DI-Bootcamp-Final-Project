from django.shortcuts import render, redirect, get_object_or_404
from .models import Properties, Favorite, PropertyImage, PropertyEditRequest, StagedImageAdd, Notification
from .forms import PropertiesForm, PropertyEditForm
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from contact.models import ContactMessage

#---retrieve all records properties table ---#
# --- Store in listings and send to HTML ---#
def property_listings(request):
    listings = Properties.objects.filter(status=Properties.StatusChoices.APPROVED).order_by("-property_ref")
    favorited_ids = set()
    favorites_count = 0

    if request.user.is_authenticated:
        # Get IDs of properties, from favorite table, favorited by the current user
        # purpose is to check/unchecked the favorite icon in each card in properties.html page
        favorited_ids = set(
            Favorite.objects.filter(user=request.user).values_list('property__property_ref', flat=True)
        )
        # purpose is to show the number of favorited properties in the favorite icon in navbar in properties.html page
        favorites_count = len(favorited_ids)

    return render(request, "properties.html", {
        "properties_list": listings,
        "favorited_ids": favorited_ids,
        "favorites_count": favorites_count,
    })

#--used for favorite icon (navbar) to show only favorited properties for current user in properties.html page--#
@login_required
def favorites_list(request):
    # Get IDs of properties, from favorite table, favorited by the current user
    favorited_ids = set(
        Favorite.objects.filter(user=request.user).values_list('property__property_ref', flat=True)
    )

    listings = Properties.objects.filter(property_ref__in=favorited_ids).order_by("-property_ref")

    return render(request, "properties.html", {"properties_list": listings,           # parameter related to cards
                                               "favorited_ids": favorited_ids,        # parameter related to favorite icon in each card (filled or unfilled)
                                               "favorites_count": len(favorited_ids), # parameter related to favorite icon in navbar (number of favorited properties)
    })

def properties(request):
    return render(request, "properties.html")

@login_required
def create_property(request):
    if request.method == "POST":
        form = PropertiesForm(request.POST, request.FILES)
        if form.is_valid():
            property_record= form.save(commit=False)
            property_record.owner = request.user.username
            property_record.save()
            # retrieve all files uploaded in the additional_images field and create a PropertyImage record for each one, linking it to the newly created property
            for img in request.FILES.getlist('additional_images'):
                PropertyImage.objects.create(property=property_record, image=img)

            #notification for the owner when they submit a property for review
            Notification.objects.create(
                user=request.user,
                message=f"Your property (Ref: {property_record.property_ref}) has been submitted for review and approval.",
                related_ref=property_record.property_ref,
            )
            return redirect('properties')
    else:
        form = PropertiesForm()

    return render(request, 'create.html', {'form': form})

def details(request):
    return render(request, "details.html")

#further propety information while clicking on property cards
def property_info(request, property_ref):
    property = get_object_or_404(Properties, property_ref=property_ref)
    contact_status = request.GET.get('contact')
    return render(request, 'propertyinfo.html', {
        'property': property,
        'contact_success': contact_status == 'success',
        'contact_error': contact_status == 'error',
    })

@require_POST
@login_required
def toggle_favorite(request, property_ref):
    property_obj = get_object_or_404(Properties, property_ref=property_ref)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
    if not created:
        favorite.delete()
    return redirect('properties')

#this view is for the sell property button in navbar
def sell_property(request):
    if request.user.is_authenticated:
        return redirect('create_property')
    return render(request, 'sell_landing.html')

#---admin dashboard view---#
@permission_required('propertylisting.change_properties', raise_exception=True)
def admin_dashboard(request):
    all_properties = Properties.objects.all().order_by('-property_ref')
    pending_properties = Properties.objects.filter(status=Properties.StatusChoices.UNDER_APPROVAL).order_by('-property_ref')
    pending_delete_properties = Properties.objects.filter(status=Properties.StatusChoices.PENDING_DELETE).order_by('-property_ref')
    pending_edits = PropertyEditRequest.objects.filter(status=PropertyEditRequest.EditStatusChoices.PENDING).select_related('property').order_by('-submitted_at')
    total_count = Properties.objects.count()
    approved_count = Properties.objects.filter(status=Properties.StatusChoices.APPROVED).count()
    pending_count = Properties.objects.filter(status=Properties.StatusChoices.UNDER_APPROVAL).count()
    rejected_count = Properties.objects.filter(status=Properties.StatusChoices.REJECTED).count()
    total_users = User.objects.count()
    total_favorites = Favorite.objects.count()
    pending_delete_count = pending_delete_properties.count()
    pending_edits_count = pending_edits.count()
    contact_messages = ContactMessage.objects.select_related('property').all()
    contact_messages_count = contact_messages.count()
    return render(request, 'admin_dashboard.html', {
        'all_properties': all_properties,
        'pending_properties': pending_properties,
        'total_count': total_count,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'total_users': total_users,
        'total_favorites': total_favorites,
        'pending_delete_properties': pending_delete_properties,
        'pending_delete_count': pending_delete_count,
        'pending_edits': pending_edits,
        'pending_edits_count': pending_edits_count,
        'contact_messages': contact_messages,
        'contact_messages_count': contact_messages_count,
    })

@require_POST
@permission_required('propertylisting.change_properties', raise_exception=True)
def approve_property(request, property_ref, action):
    property_obj = get_object_or_404(Properties, property_ref=property_ref)
    if action == 'approve':
        property_obj.status = Properties.StatusChoices.APPROVED
        #if admin approves the property, create a notification for the owner to inform them
        property_obj.save()
        owner_user = User.objects.filter(username=property_obj.owner).first()
        if owner_user:
            Notification.objects.create(
                user=owner_user,
                message=f"Your property (Ref: {property_obj.property_ref}) has been approved and is now live.",
                related_ref=property_obj.property_ref,
            )
    elif action == 'reject':
        property_obj.status = Properties.StatusChoices.REJECTED
        #if admin rejects the property, create a notification for the owner to inform them
        property_obj.save()
        owner_user = User.objects.filter(username=property_obj.owner).first()
        if owner_user:
            Notification.objects.create(
                user=owner_user,
                message=f"Your property (Ref: {property_obj.property_ref}) has been rejected.",
                related_ref=property_obj.property_ref,
            )
    return redirect('admin_dashboard')

#---owner dashboard: track own property submissions---#
@login_required
def my_submissions(request):
    my_properties = Properties.objects.filter(owner=request.user.username).order_by('-property_ref')
    approved_count = my_properties.filter(status=Properties.StatusChoices.APPROVED).count()
    pending_count = my_properties.filter(status=Properties.StatusChoices.UNDER_APPROVAL).count()
    rejected_count = my_properties.filter(status=Properties.StatusChoices.REJECTED).count()
    pending_delete_count = my_properties.filter(status=Properties.StatusChoices.PENDING_DELETE).count()
    pending_edit_refs = set(
        PropertyEditRequest.objects.filter(
            property__owner=request.user.username,
            status=PropertyEditRequest.EditStatusChoices.PENDING
        ).values_list('property__property_ref', flat=True)
    )
    pending_edit_count = len(pending_edit_refs)

    return render(request, 'my_submissions.html', {
        'my_properties': my_properties,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'pending_delete_count': pending_delete_count,
        'pending_edit_refs': pending_edit_refs,
        'pending_edit_count': pending_edit_count,
    })

@login_required
def my_properties(request):
    favorited_ids = set(
        Favorite.objects.filter(user=request.user).values_list('property__property_ref', flat=True)
    )
    listings = Properties.objects.filter(
        owner=request.user.username,
        status=Properties.StatusChoices.APPROVED
    ).order_by("-property_ref")

    return render(request, "properties.html", {
        "properties_list": listings,
        "favorited_ids": favorited_ids,
        "favorites_count": len(favorited_ids),
    })

# when property owner clicks "Request Deletion", the property status changes to "Pending Delete" and a notification is sent to admin
@require_POST
@login_required
def request_deletion(request, property_ref):
    property_obj = get_object_or_404(Properties, property_ref=property_ref)
    if property_obj.owner != request.user.username:
        return redirect('my_submissions')
    allowed_statuses = [Properties.StatusChoices.APPROVED, Properties.StatusChoices.REJECTED, Properties.StatusChoices.UNDER_APPROVAL]
    if property_obj.status in allowed_statuses:
        property_obj.previous_status = property_obj.status
        property_obj.status = Properties.StatusChoices.PENDING_DELETE
        property_obj.save()
        #Notification
        owner_user = User.objects.filter(username=property_obj.owner).first()
        if owner_user:
            Notification.objects.create(
                user=owner_user,
                message=f"Your property (Ref: {property_obj.property_ref}) has been requested for deletion.",
                related_ref=property_obj.property_ref,
            )
    return redirect('my_submissions')

#---owner cancels their own pending deletion request---#
@require_POST
@login_required
def cancel_deletion_request(request, property_ref):
    property_obj = get_object_or_404(Properties, property_ref=property_ref)
    if property_obj.owner != request.user.username:
        return redirect('my_submissions')
    if property_obj.status != Properties.StatusChoices.PENDING_DELETE:
        return redirect('my_submissions')
    property_obj.status = property_obj.previous_status
    property_obj.previous_status = ''
    property_obj.save()
    return redirect('my_submissions')

#---admin confirms or rejects a deletion request---#
@require_POST
@permission_required('propertylisting.change_properties', raise_exception=True)
def process_deletion(request, property_ref, action):
    property_obj = get_object_or_404(Properties, property_ref=property_ref)
    if action == 'confirm':
        property_obj.delete()
        #notification
        owner_user = User.objects.filter(username=property_obj.owner).first()
        if owner_user:
            Notification.objects.create(
                user=owner_user,
                message=f"Your property (Ref: {property_obj.property_ref}) has been deleted by admin.",
                related_ref=property_obj.property_ref,
            )
    elif action == 'reject':
        property_obj.status = property_obj.previous_status
        property_obj.previous_status = ''
        property_obj.save()

        owner_user = User.objects.filter(username=property_obj.owner).first()
        if owner_user:
            Notification.objects.create(
                user=owner_user,
                message=f"Your request to delete property (Ref: {property_obj.property_ref}) has been rejected.",
                related_ref=property_obj.property_ref,
            )
    return redirect('admin_dashboard')

#---owner submits an edit request (staged, not live until admin approves)---#
@login_required
def edit_property(request, property_ref):
    property_obj = get_object_or_404(Properties, property_ref=property_ref)
    if property_obj.owner != request.user.username:
        return redirect('my_submissions')

    editable_statuses = [Properties.StatusChoices.APPROVED, Properties.StatusChoices.REJECTED]
    if property_obj.status not in editable_statuses:
        return redirect('my_submissions')

    #when 'submit for review' is clicked
    if request.method == 'POST':
        form = PropertyEditForm(request.POST, request.FILES)
        if form.is_valid():
            pks_to_delete = request.POST.getlist('delete_image')
            new_images    = request.FILES.getlist('new_images')

            # Update existing pending edit if one exists, otherwise create
            edit_req = PropertyEditRequest.objects.filter(
                property=property_obj,
                status=PropertyEditRequest.EditStatusChoices.PENDING
            ).first()
            if edit_req:
                edit_req.title       = form.cleaned_data['title']
                edit_req.location    = form.cleaned_data['location']
                edit_req.price       = form.cleaned_data['price']
                edit_req.description = form.cleaned_data['description']
                edit_req.rooms       = form.cleaned_data['rooms']
                edit_req.bedrooms    = form.cleaned_data['bedrooms']
                edit_req.area        = form.cleaned_data['area']
                if form.cleaned_data.get('image'):
                    edit_req.image = form.cleaned_data['image']
                edit_req.image_pks_to_delete = ','.join(pks_to_delete)
                edit_req.save()
                edit_req.staged_images_to_add.all().delete()
            else:
                edit_req = form.save(commit=False)
                edit_req.property = property_obj
                edit_req.image_pks_to_delete = ','.join(pks_to_delete)
                edit_req.save()

            for img in new_images:
                StagedImageAdd.objects.create(request=edit_req, image=img)

            return redirect('my_submissions')
    else:   
        pending_edit = PropertyEditRequest.objects.filter(
            property=property_obj,
            status=PropertyEditRequest.EditStatusChoices.PENDING
        ).first()

        source = pending_edit if pending_edit else property_obj
        
        initial = {
            'title': source.title,
            'location': source.location,
            'price': source.price,
            'description': source.description,
            'rooms': source.rooms,
            'bedrooms': source.bedrooms,
            'area': source.area,
        }
        form = PropertyEditForm(initial=initial)

    current_images = property_obj.additional_images.all()
    delete_pk_set = set()
    staged_to_add = []
    staged_main_image = None
    if pending_edit:
        delete_pk_set = set(pk.strip() for pk in pending_edit.image_pks_to_delete.split(',') if pk.strip())
        staged_to_add = list(pending_edit.staged_images_to_add.all())
        staged_main_image = pending_edit.image if pending_edit.image else None

    return render(request, 'edit_property.html', {
        'form': form,
        'property': property_obj,
        'staged_main_image': staged_main_image,
        'current_images': current_images,
        'delete_pk_set': delete_pk_set,
        'staged_to_add': staged_to_add,
    })

#---admin review page: side-by-side comparison of current vs proposed fields---#
@login_required
@permission_required('propertylisting.change_properties', raise_exception=True)
def review_edit(request, edit_id):
    edit_req = get_object_or_404(PropertyEditRequest, pk=edit_id)
    prop = edit_req.property

    fields = [
        ('Title',       prop.title,       edit_req.title),
        ('Location',    prop.location,    edit_req.location),
        ('Price (MUR)', prop.price,       edit_req.price),
        ('Description', prop.description, edit_req.description),
        ('Rooms',       prop.rooms,       edit_req.rooms),
        ('Bedrooms',    prop.bedrooms,    edit_req.bedrooms),
        ('Area (sqft)', prop.area,        edit_req.area),
    ]
    comparison = [
        {'label': label, 'current': str(current), 'proposed': str(proposed), 'changed': str(current) != str(proposed)}
        for label, current, proposed in fields
    ]

    return render(request, 'review_edit.html', {
        'edit_req': edit_req,
        'property': prop,
        'comparison': comparison,
        'delete_pk_set': set(pk.strip() for pk in edit_req.image_pks_to_delete.split(',') if pk.strip()),
    })

#---admin approves or rejects an edit request---#
@require_POST
@permission_required('propertylisting.change_properties', raise_exception=True)
def approve_edit(request, edit_id, action):
    edit_req = get_object_or_404(PropertyEditRequest, pk=edit_id)
    property_obj = edit_req.property

    if action == 'approve':
        property_obj.title       = edit_req.title
        property_obj.location    = edit_req.location
        property_obj.price       = edit_req.price
        property_obj.description = edit_req.description
        property_obj.rooms       = edit_req.rooms
        property_obj.bedrooms    = edit_req.bedrooms
        property_obj.area        = edit_req.area
        if edit_req.image:
            property_obj.image = edit_req.image
        # Apply any staged additional image changes
        if edit_req.image_pks_to_delete:
            pk_list = [int(pk) for pk in edit_req.image_pks_to_delete.split(',') if pk.strip()]
            PropertyImage.objects.filter(pk__in=pk_list, property=property_obj).delete()
        for staged in edit_req.staged_images_to_add.all():
            PropertyImage.objects.create(property=property_obj, image=staged.image)
        if property_obj.status == Properties.StatusChoices.REJECTED:
            property_obj.status = Properties.StatusChoices.APPROVED
        property_obj.save()
        edit_req.status = PropertyEditRequest.EditStatusChoices.APPROVED
    elif action == 'reject':
        edit_req.status = PropertyEditRequest.EditStatusChoices.REJECTED

    edit_req.save()
    return redirect('admin_dashboard')

#---manage_images redirects to unified edit page---#
@login_required
def manage_images(request, property_ref):
    return redirect('edit_property', property_ref=property_ref)

#---mark a single notification as read---#
@require_POST
@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'properties'))

#---mark all notifications as read---#
@require_POST
@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'properties'))