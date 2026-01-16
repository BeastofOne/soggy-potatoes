from django.contrib import admin
from .models import UserProfile, PetPhoto


class PetPhotoInline(admin.TabularInline):
    model = PetPhoto
    extra = 1
    readonly_fields = ['uploaded_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'has_pets', 'pet_count', 'created_at']
    list_filter = ['has_pets', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio', 'location', 'pet_names']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PetPhotoInline]

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('About', {
            'fields': ('bio', 'location', 'avatar', 'website')
        }),
        ('Pet Information', {
            'fields': ('has_pets', 'pet_count', 'pet_names', 'pet_types', 'favorite_pet_story')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PetPhoto)
class PetPhotoAdmin(admin.ModelAdmin):
    list_display = ['profile', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['profile__user__username', 'caption']
    readonly_fields = ['uploaded_at']
