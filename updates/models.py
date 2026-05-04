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


# Redwan's Work:
class ChatRoom(models.Model):
    """
    A chat room for group discussions or direct messaging.
    Pre-created rooms exist for software, banking, healthcare industries.
    """
    ROOM_TYPE_CHOICES = [
        ('software', 'Software Engineering'),
        ('banking', 'Banking & Finance'),
        ('healthcare', 'Healthcare'),
        ('general', 'General'),
        ('direct', 'Direct Message'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='general')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_rooms')
    member_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class ChatRoomMember(models.Model):
    """
    Tracks which users are members of which chat rooms.
    """
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat_room', 'user')

    def __str__(self):
        return f"{self.user.name} in {self.chat_room.name}"


class ChatMessage(models.Model):
    """
    A message sent in a chat room.
    Supports soft-delete (message stays in DB but shows as deleted).
    """
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender.name}: {self.content[:30]}"
