from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max
from django.utils import timezone

from .models import Conversation, Message, Notification
from .filters import filter_content


@login_required
def inbox_view(request):
    """Display user's message inbox."""
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')

    # Add extra info for each conversation
    conversation_data = []
    for conv in conversations:
        other_user = conv.get_other_participant(request.user)
        last_msg = conv.last_message()
        unread = conv.unread_count_for_user(request.user)
        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_msg,
            'unread_count': unread,
        })

    context = {
        'conversations': conversation_data,
    }
    return render(request, 'messaging/inbox.html', context)


@login_required
def conversation_view(request, conversation_id):
    """Display a conversation and its messages."""
    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id,
        participants=request.user
    )

    # Mark messages as read
    conversation.messages.filter(is_read=False).exclude(
        sender=request.user
    ).update(is_read=True)

    # Mark related notifications as read
    Notification.objects.filter(
        user=request.user,
        conversation=conversation,
        is_read=False
    ).update(is_read=True)

    other_user = conversation.get_other_participant(request.user)
    all_messages = conversation.messages.select_related('sender').all()

    context = {
        'conversation': conversation,
        'other_user': other_user,
        'messages': all_messages,
    }
    return render(request, 'messaging/conversation.html', context)


@login_required
def new_conversation_view(request, username):
    """Start or continue a conversation with a user."""
    other_user = get_object_or_404(User, username=username)

    # Can't message yourself
    if other_user == request.user:
        messages.error(request, "You can't message yourself!")
        return redirect('users:public_profile', username=username)

    # Check if conversation already exists
    existing = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if existing:
        return redirect('messaging:conversation', conversation_id=existing.pk)

    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)

    return redirect('messaging:conversation', conversation_id=conversation.pk)


@login_required
def send_message(request, conversation_id):
    """Send a message in a conversation."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id,
        participants=request.user
    )

    content = request.POST.get('content', '').strip()
    image = request.FILES.get('image')

    if not content and not image:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    # Filter content
    original_content = content
    filtered_content, was_filtered = filter_content(content)

    # Create message
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=filtered_content,
        image=image,
        is_filtered=was_filtered,
        original_content=original_content if was_filtered else '',
    )

    # Update conversation timestamp
    conversation.updated_at = timezone.now()
    conversation.save()

    # Create notification for other user
    other_user = conversation.get_other_participant(request.user)
    if other_user:
        Notification.objects.create(
            user=other_user,
            notification_type='message',
            title=f'New message from {request.user.username}',
            message=filtered_content[:100] + '...' if len(filtered_content) > 100 else filtered_content,
            link=f'/messages/conversation/{conversation.pk}/',
            from_user=request.user,
            conversation=conversation,
        )

    # Return JSON for AJAX or redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.pk,
                'content': message.content,
                'image': message.image.url if message.image else None,
                'sender': request.user.username,
                'created_at': message.created_at.strftime('%b %d, %Y %I:%M %p'),
                'is_filtered': was_filtered,
            }
        })

    return redirect('messaging:conversation', conversation_id=conversation_id)


@login_required
def poll_messages(request, conversation_id):
    """Poll for new messages (AJAX endpoint)."""
    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id,
        participants=request.user
    )

    after_id = int(request.GET.get('after', 0))
    new_messages = conversation.messages.filter(pk__gt=after_id).select_related('sender')

    # Mark as read
    new_messages.exclude(sender=request.user).update(is_read=True)

    return JsonResponse({
        'messages': [{
            'id': m.pk,
            'sender': m.sender.username,
            'sender_is_admin': m.sender.is_superuser,
            'content': m.content,
            'image': m.image.url if m.image else None,
            'created_at': m.created_at.strftime('%b %d, %Y %I:%M %p'),
            'is_mine': m.sender == request.user,
        } for m in new_messages]
    })


@login_required
def notifications_view(request):
    """Display all notifications."""
    notifications = Notification.objects.filter(user=request.user)

    context = {
        'notifications': notifications,
    }
    return render(request, 'messaging/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read."""
    notification = get_object_or_404(
        Notification,
        pk=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # Redirect to the notification's link if it has one
    if notification.link:
        return redirect(notification.link)
    return redirect('messaging:notifications')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('messaging:notifications')


@login_required
def notification_count(request):
    """Return unread notification count (AJAX)."""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    message_count = 0

    # Count unread messages across all conversations
    for conv in Conversation.objects.filter(participants=request.user):
        message_count += conv.unread_count_for_user(request.user)

    return JsonResponse({
        'notification_count': count,
        'message_count': message_count,
        'total': count + message_count,
    })
