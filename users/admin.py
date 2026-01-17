from django.contrib import admin
from .models import UserProfile, PetPhoto, ReservedUsername, Badge, UserBadge, UserBan, PostReport


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


@admin.register(ReservedUsername)
class ReservedUsernameAdmin(admin.ModelAdmin):
    list_display = ['username', 'reason', 'created_at']
    search_fields = ['username', 'reason']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'awarded_by', 'awarded_at']
    list_filter = ['badge', 'awarded_at']
    search_fields = ['user__username', 'badge__name']
    readonly_fields = ['awarded_at']


@admin.register(UserBan)
class UserBanAdmin(admin.ModelAdmin):
    list_display = ['user', 'reason', 'banned_by', 'banned_at', 'expires_at', 'is_active']
    list_filter = ['banned_at', 'expires_at']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['banned_at']


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reason', 'status', 'created_at', 'reviewed_by']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['reporter__username', 'details']
    readonly_fields = ['created_at', 'reviewed_at']
