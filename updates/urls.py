from django.urls import path
from . import views

urlpatterns = [
    # Notifications
    path('notifications/', views.notifications_list_view, name='notifications_list'),
    path('notifications/read/<int:notif_id>/', views.mark_notification_read_view, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_read_view, name='mark_all_read'),

    # Chat Rooms
    path('chat/', views.chat_rooms_list_view, name='chat_rooms_list'),
    path('chat/create/', views.create_room_view, name='create_room'),
    path('chat/join/<int:room_id>/', views.join_room_view, name='join_room'),
    path('chat/leave/<int:room_id>/', views.leave_room_view, name='leave_room'),
    path('chat/rename/<int:room_id>/', views.rename_room_view, name='rename_room'),
    path('chat/room/<int:room_id>/', views.chat_room_window_view, name='chat_room_window'),

    # Messaging
    path('chat/message/edit/<int:message_id>/', views.edit_message_view, name='edit_message'),
    path('chat/message/delete/<int:message_id>/', views.delete_message_view, name='delete_message'),

    # Direct Messages
    path('chat/dm/<int:user_id>/', views.start_direct_message_view, name='start_direct_message'),
    path('chat/my-dms/', views.my_direct_messages_view, name='my_direct_messages'),
]
