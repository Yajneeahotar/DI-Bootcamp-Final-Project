from django.shortcuts import render, redirect, get_object_or_404
from .models import Properties, Favorite, PropertyImage
from .forms import PropertiesForm
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

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
            return redirect('properties')
    else:
        form = PropertiesForm()

    return render(request, 'create.html', {'form': form})

def details(request):
    return render(request, "details.html")

#further propety information while clicking on property cards
def property_info(request, property_ref):
    property = get_object_or_404(Properties, property_ref=property_ref)
    return render(request, 'propertyinfo.html', {'property': property})

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
    total_count = Properties.objects.count()
    approved_count = Properties.objects.filter(status=Properties.StatusChoices.APPROVED).count()
    pending_count = Properties.objects.filter(status=Properties.StatusChoices.UNDER_APPROVAL).count()
    rejected_count = Properties.objects.filter(status=Properties.StatusChoices.REJECTED).count()
    total_users = User.objects.count()
    total_favorites = Favorite.objects.count()
    pending_delete_count = pending_delete_properties.count()
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
    })

@require_POST
@permission_required('propertylisting.change_properties', raise_exception=True)
def approve_property(request, property_ref, action):
    property_obj = get_object_or_404(Properties, property_ref=property_ref)
    if action == 'approve':
        property_obj.status = Properties.StatusChoices.APPROVED
    elif action == 'reject':
        property_obj.status = Properties.StatusChoices.REJECTED
    property_obj.save()
    return redirect('admin_dashboard')

#---owner dashboard: track own property submissions---#
@login_required
def my_submissions(request):
    my_properties = Properties.objects.filter(owner=request.user.username).order_by('-property_ref')
    approved_count = my_properties.filter(status=Properties.StatusChoices.APPROVED).count()
    pending_count = my_properties.filter(status=Properties.StatusChoices.UNDER_APPROVAL).count()
    rejected_count = my_properties.filter(status=Properties.StatusChoices.REJECTED).count()
    pending_delete_count = my_properties.filter(status=Properties.StatusChoices.PENDING_DELETE).count()

    return render(request, 'my_submissions.html', {
        'my_properties': my_properties,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'pending_delete_count': pending_delete_count,
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
    elif action == 'reject':
        property_obj.status = property_obj.previous_status
        property_obj.previous_status = ''
        property_obj.save()
    return redirect('admin_dashboard')