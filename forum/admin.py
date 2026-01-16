from django.contrib import admin
from .models import ForumCategory, Thread, Post, Reaction


@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'thread_count', 'post_count', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    readonly_fields = ['author', 'created_at', 'is_edited']
    fields = ['author', 'content', 'created_at', 'is_edited']


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'reply_count', 'views', 'score', 'is_pinned', 'is_locked', 'created_at']
    list_filter = ['category', 'is_pinned', 'is_locked', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_pinned', 'is_locked']
    inlines = [PostInline]
    readonly_fields = ['views', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('category', 'author', 'title', 'slug', 'content')
        }),
        ('Status', {
            'fields': ('is_pinned', 'is_locked', 'views')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'author', 'thread', 'score', 'is_edited', 'created_at']
    list_filter = ['is_edited', 'created_at']
    search_fields = ['content', 'author__username', 'thread__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'reaction_type', 'get_target', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username']

    def get_target(self, obj):
        if obj.thread:
            return f"Thread: {obj.thread.title}"
        return f"Post in: {obj.post.thread.title}"
    get_target.short_description = 'Target'
