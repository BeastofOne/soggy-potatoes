from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    """A conversation between two users."""
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        usernames = ', '.join([u.username for u in self.participants.all()[:2]])
        return f"Conversation: {usernames}"

    def get_other_participant(self, user):
        """Get the other user in the conversation."""
        return self.participants.exclude(pk=user.pk).first()

    def unread_count_for_user(self, user):
        """Count unread messages for a user."""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def last_message(self):
        """Get the most recent message."""
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """A message in a conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(max_length=5000)
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    is_filtered = models.BooleanField(default=False)  # True if content was filtered
    original_content = models.TextField(blank=True)  # Store original if filtered
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"


class Notification(models.Model):
    """User notification for various events."""
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('order', 'Order Update'),
        ('forum', 'Forum Reply'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional references
    from_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='triggered_notifications'
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title}"


class BlockedWord(models.Model):
    """Words/phrases to filter from messages (NSFW/dangerous content)."""
    CATEGORY_CHOICES = [
        ('nsfw', 'NSFW Content'),
        ('dangerous', 'Dangerous/Harmful'),
        ('spam', 'Spam'),
        ('profanity', 'Profanity'),
        ('other', 'Other'),
    ]

    word = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.word} ({self.category})"

    class Meta:
        ordering = ['word']
