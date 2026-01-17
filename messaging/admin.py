from django.contrib import admin
from .models import Conversation, Message, Notification, BlockedWord
from .filters import invalidate_filter_cache


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'content', 'image', 'is_read', 'is_filtered', 'created_at']
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_participants', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['participants__username']
    inlines = [MessageInline]

    def get_participants(self, obj):
        return ', '.join([u.username for u in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'short_content', 'is_read', 'is_filtered', 'created_at']
    list_filter = ['is_read', 'is_filtered', 'created_at']
    search_fields = ['sender__username', 'content']
    readonly_fields = ['original_content']

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']


@admin.register(BlockedWord)
class BlockedWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['word']
    list_editable = ['is_active']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        invalidate_filter_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        invalidate_filter_cache()
