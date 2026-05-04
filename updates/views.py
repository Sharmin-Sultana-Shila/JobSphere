from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Notification, ChatRoom, ChatRoomMember, ChatMessage
from .utils import create_notification


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


# ===================================================================
# STORY-19: Chat Rooms
# ===================================================================

def chat_rooms_list_view(request):
    """
    Shows all available chat rooms with join/leave buttons.
    Industry rooms first, then custom rooms. Direct message rooms are excluded.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    # Get all rooms except direct messages
    rooms = ChatRoom.objects.exclude(room_type='direct')

    # Get rooms the user has joined
    joined_room_ids = ChatRoomMember.objects.filter(
        user=request.user
    ).values_list('chat_room_id', flat=True)

    # Add joined flag to each room
    rooms_data = []
    for room in rooms:
        rooms_data.append({
            'room': room,
            'is_joined': room.id in joined_room_ids,
        })

    return render(request, 'updates/chat_rooms_list.html', {
        'rooms_data': rooms_data,
        'joined_room_ids': joined_room_ids,
    })


def join_room_view(request, room_id):
    """
    User joins a chat room.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    room = get_object_or_404(ChatRoom, id=room_id)

    # Check if already a member
    if not ChatRoomMember.objects.filter(chat_room=room, user=request.user).exists():
        ChatRoomMember.objects.create(chat_room=room, user=request.user)
        room.member_count = room.member_count + 1
        room.save()
        messages.success(request, f'You joined "{room.name}".')
    else:
        messages.error(request, 'You are already a member of this room.')

    return redirect('chat_rooms_list')


def leave_room_view(request, room_id):
    """
    User leaves a chat room.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    room = get_object_or_404(ChatRoom, id=room_id)

    membership = ChatRoomMember.objects.filter(chat_room=room, user=request.user)
    if membership.exists():
        membership.delete()
        if room.member_count > 0:
            room.member_count = room.member_count - 1
            room.save()
        messages.success(request, f'You left "{room.name}".')
    else:
        messages.error(request, 'You are not a member of this room.')

    return redirect('chat_rooms_list')


def create_room_view(request):
    """
    User creates a custom chat room.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'Room name is required.')
            return redirect('create_room')

        room = ChatRoom.objects.create(
            name=name,
            description=description,
            room_type='general',
            created_by=request.user,
            member_count=1
        )

        # Auto-join the creator
        ChatRoomMember.objects.create(chat_room=room, user=request.user)

        messages.success(request, f'Room "{name}" created!')
        return redirect('chat_room_window', room_id=room.id)

    return render(request, 'updates/create_room.html')


def rename_room_view(request, room_id):
    """
    Room creator can rename their room.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    room = get_object_or_404(ChatRoom, id=room_id)

    if room.created_by != request.user:
        messages.error(request, 'Only the room creator can rename this room.')
        return redirect('chat_room_window', room_id=room_id)

    if request.method == 'POST':
        new_name = request.POST.get('name', '').strip()
        if new_name:
            room.name = new_name
            room.save()
            messages.success(request, 'Room renamed successfully.')
        else:
            messages.error(request, 'Room name cannot be empty.')

    return redirect('chat_room_window', room_id=room_id)


# ===================================================================
# STORY-20: Messaging
# ===================================================================

def chat_room_window_view(request, room_id):
    """
    Chat room window showing all messages.
    User can send a message. Members sidebar shows all members.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    room = get_object_or_404(ChatRoom, id=room_id)

    # Check if user is a member
    is_member = ChatRoomMember.objects.filter(chat_room=room, user=request.user).exists()

    # Get all messages
    chat_messages = ChatMessage.objects.filter(chat_room=room).select_related('sender')

    # Get all members
    members = ChatRoomMember.objects.filter(chat_room=room).select_related('user')

    # Handle sending a message
    if request.method == 'POST' and is_member:
        content = request.POST.get('content', '').strip()
        if content:
            ChatMessage.objects.create(
                chat_room=room,
                sender=request.user,
                content=content
            )

            # Notify other members about the new message
            for member in members:
                if member.user != request.user:
                    create_notification(
                        user=member.user,
                        notif_type='chat',
                        title=f'New message in {room.name}',
                        content=f'{request.user.name}: {content[:80]}...' if len(content) > 80 else f'{request.user.name}: {content}'
                    )

            return redirect('chat_room_window', room_id=room_id)

    return render(request, 'updates/chat_room_window.html', {
        'room': room,
        'chat_messages': chat_messages,
        'members': members,
        'is_member': is_member,
    })


def edit_message_view(request, message_id):
    """
    User edits their own message.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    msg = get_object_or_404(ChatMessage, id=message_id, sender=request.user)

    if msg.is_deleted:
        messages.error(request, 'Cannot edit a deleted message.')
        return redirect('chat_room_window', room_id=msg.chat_room.id)

    if request.method == 'POST':
        new_content = request.POST.get('content', '').strip()
        if new_content:
            msg.content = new_content
            msg.save()
            messages.success(request, 'Message edited.')
        else:
            messages.error(request, 'Message cannot be empty.')

    return redirect('chat_room_window', room_id=msg.chat_room.id)


def delete_message_view(request, message_id):
    """
    User soft-deletes their own message.
    Message stays in DB but content is hidden.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    msg = get_object_or_404(ChatMessage, id=message_id, sender=request.user)

    msg.is_deleted = True
    msg.save()
    messages.success(request, 'Message deleted.')

    return redirect('chat_room_window', room_id=msg.chat_room.id)


def start_direct_message_view(request, user_id):
    """
    Start a direct message between current user and another user.
    If DM room already exists, redirect to it. Otherwise create a new one.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    from users.models import User
    other_user = get_object_or_404(User, id=user_id)

    # Don't DM yourself
    if other_user == request.user:
        messages.error(request, 'You cannot message yourself.')
        return redirect('chat_rooms_list')

    # Check if a DM room already exists between these two users
    my_dm_rooms = ChatRoom.objects.filter(room_type='direct', members__user=request.user)
    existing_room = None
    for room in my_dm_rooms:
        if ChatRoomMember.objects.filter(chat_room=room, user=other_user).exists():
            existing_room = room
            break

    if existing_room:
        return redirect('chat_room_window', room_id=existing_room.id)

    # Create a new DM room
    room = ChatRoom.objects.create(
        name=f'{request.user.name} & {other_user.name}',
        description='Direct message',
        room_type='direct',
        created_by=request.user,
        member_count=2
    )

    ChatRoomMember.objects.create(chat_room=room, user=request.user)
    ChatRoomMember.objects.create(chat_room=room, user=other_user)

    return redirect('chat_room_window', room_id=room.id)


def my_direct_messages_view(request):
    """
    Shows all direct message conversations for the current user.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    # Get all DM rooms where user is a member
    dm_room_ids = ChatRoomMember.objects.filter(
        user=request.user,
        chat_room__room_type='direct'
    ).values_list('chat_room_id', flat=True)

    dm_rooms = ChatRoom.objects.filter(id__in=dm_room_ids)

    # Get the other person's name for each DM room
    dm_data = []
    for room in dm_rooms:
        other_member = ChatRoomMember.objects.filter(
            chat_room=room
        ).exclude(user=request.user).select_related('user').first()

        # Get last message
        last_msg = ChatMessage.objects.filter(chat_room=room).order_by('-sent_at').first()

        dm_data.append({
            'room': room,
            'other_user': other_member.user if other_member else None,
            'last_message': last_msg,
        })

    return render(request, 'updates/direct_messages.html', {
        'dm_data': dm_data
    })
