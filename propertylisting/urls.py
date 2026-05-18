from django.urls import path
from . import views

urlpatterns = [
    path('properties_list/', views.property_listings, name='properties'),
    path('favorites/', views.favorites_list, name='my_favorites'),
    path('add/', views.create_property, name='create_property'),
    path('details/', views.details, name='details'),
    path('info/<str:property_ref>/', views.property_info, name='property_info'),
    path('favorite/<str:property_ref>/', views.toggle_favorite, name='toggle_favorite'),
    path('sell/', views.sell_property, name='sell_property'),
    path('approve/<str:property_ref>/<str:action>/', views.approve_property, name='approve_property'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('my-properties/', views.my_properties, name='my_properties'),
    path('request-deletion/<str:property_ref>/', views.request_deletion, name='request_deletion'),
    path('cancel-deletion/<str:property_ref>/', views.cancel_deletion_request, name='cancel_deletion_request'),
    path('process-deletion/<str:property_ref>/<str:action>/', views.process_deletion, name='process_deletion'),
    path('edit/<str:property_ref>/', views.edit_property, name='edit_property'),
    path('approve-edit/<int:edit_id>/<str:action>/', views.approve_edit, name='approve_edit'),
    path('review-edit/<int:edit_id>/', views.review_edit, name='review_edit'),
    path('manage-images/<str:property_ref>/', views.manage_images, name='manage_images'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]