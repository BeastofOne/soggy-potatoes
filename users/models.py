from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile with bio and pet information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')

    # About Me
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself!")
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Pet Info
    has_pets = models.BooleanField(default=False)
    pet_count = models.PositiveIntegerField(default=0)
    pet_names = models.CharField(max_length=200, blank=True, help_text="Names of your pets")
    pet_types = models.CharField(max_length=200, blank=True, help_text="e.g., 2 cats, 1 dog")
    favorite_pet_story = models.TextField(max_length=1000, blank=True)

    # Social
    website = models.URLField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class PetPhoto(models.Model):
    """Photos of user's pets."""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='pet_photos')
    image = models.ImageField(upload_to='pet_photos/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pet photo by {self.profile.user.username}"

    class Meta:
        ordering = ['-uploaded_at']


class ReservedUsername(models.Model):
    """Usernames that cannot be registered."""
    username = models.CharField(max_length=150, unique=True)
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']


class Badge(models.Model):
    """Custom badge that superusers can award to users."""
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='badges/')
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_badges')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class UserBadge(models.Model):
    """Badge awarded to a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awarded_to')
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='badges_awarded')

    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.badge.name} awarded to {self.user.username}"


class UserBan(models.Model):
    """Record of banned users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ban')
    reason = models.TextField()
    banned_at = models.DateTimeField(auto_now_add=True)
    banned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bans_issued')
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Leave blank for permanent ban")

    def __str__(self):
        return f"{self.user.username} banned by {self.banned_by}"

    @property
    def is_active(self):
        """Check if ban is currently active."""
        from django.utils import timezone
        if self.expires_at is None:
            return True  # Permanent ban
        return timezone.now() < self.expires_at


class PostReport(models.Model):
    """Report of a forum post by a user."""
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
        ('action_taken', 'Action Taken'),
    ]

    # Can report either a thread or a post
    thread = models.ForeignKey('forum.Thread', on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    post = models.ForeignKey('forum.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='reports')

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    details = models.TextField(blank=True, help_text="Additional details about the report")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = f"thread: {self.thread.title}" if self.thread else f"post in: {self.post.thread.title}"
        return f"Report by {self.reporter.username} on {target}"
