from .models import Notification


def unread_notifications(request):
    """
    Makes unread notification count available to all templates.
    Adds 'unread_notif_count' variable to every template context.
    """
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notif_count': count}
    return {'unread_notif_count': 0}
