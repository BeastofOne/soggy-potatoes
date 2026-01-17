from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Inbox
    path('inbox/', views.inbox_view, name='inbox'),

    # Conversations
    path('conversation/<int:conversation_id>/', views.conversation_view, name='conversation'),
    path('conversation/new/<str:username>/', views.new_conversation_view, name='new_conversation'),

    # AJAX endpoints
    path('send/<int:conversation_id>/', views.send_message, name='send_message'),
    path('poll/<int:conversation_id>/', views.poll_messages, name='poll_messages'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_read'),
    path('notifications/count/', views.notification_count, name='notification_count'),
]
