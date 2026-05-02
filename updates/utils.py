from .models import Notification


def create_notification(user, notif_type, title, content):
    """
    Helper function to create a notification for a user.
    Called from various views whenever a notification event occurs.

    notif_type choices: jobMatch, status, interview, chat
    """
    Notification.objects.create(
        user=user,
        notif_type=notif_type,
        title=title,
        content=content,
        is_read=False
    )
