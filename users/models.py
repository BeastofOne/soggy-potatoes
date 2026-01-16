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
