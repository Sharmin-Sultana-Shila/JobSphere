from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Notification


def notifications_list_view(request):
    """
    Shows all notifications for the logged-in user sorted by most recent.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'updates/notifications_list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })


def mark_notification_read_view(request, notif_id):
    """
    Marks a single notification as read.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()

    return redirect('notifications_list')


def mark_all_read_view(request):
    """
    Marks all notifications as read for the current user.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications_list')
