from django.db import models
from users.models import User


class Notification(models.Model):
    """
    In-app notification for a user.
    Triggered by application status changes, interviews, chat, etc.
    """
    TYPE_CHOICES = [
        ('jobMatch', 'Job Match'),
        ('status', 'Status Update'),
        ('interview', 'Interview'),
        ('chat', 'Chat Message'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='status')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"
