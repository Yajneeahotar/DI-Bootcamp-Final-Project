from .models import Notification


def notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False)
        return {
            'user_notifications': unread,
            'unread_notifications_count': unread.count(),
        }
    return {
        'user_notifications': [],
        'unread_notifications_count': 0,
    }
