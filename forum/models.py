from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class ForumCategory(models.Model):
    """Forum category for organizing discussions."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-chat-dots')  # Bootstrap icon class
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Forum Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('forum:category', kwargs={'slug': self.slug})

    @property
    def thread_count(self):
        return self.threads.count()

    @property
    def post_count(self):
        return Post.objects.filter(thread__category=self).count()

    @property
    def latest_post(self):
        return Post.objects.filter(thread__category=self).order_by('-created_at').first()


class Thread(models.Model):
    """Forum thread/topic."""
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='threads')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_threads')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        unique_together = ['category', 'slug']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Thread.objects.filter(category=self.category, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('forum:thread', kwargs={
            'category_slug': self.category.slug,
            'thread_slug': self.slug
        })

    @property
    def reply_count(self):
        return self.posts.count() - 1  # Exclude the original post

    @property
    def latest_post(self):
        return self.posts.order_by('-created_at').first()

    @property
    def upvote_count(self):
        return self.reactions.filter(reaction_type='upvote').count()

    @property
    def downvote_count(self):
        return self.reactions.filter(reaction_type='downvote').count()

    @property
    def score(self):
        return self.upvote_count - self.downvote_count


class Post(models.Model):
    """Reply/post in a thread."""
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Post by {self.author.username} in {self.thread.title}"

    @property
    def upvote_count(self):
        return self.reactions.filter(reaction_type='upvote').count()

    @property
    def downvote_count(self):
        return self.reactions.filter(reaction_type='downvote').count()

    @property
    def score(self):
        return self.upvote_count - self.downvote_count


class Reaction(models.Model):
    """Reaction (upvote/downvote) on threads or posts."""
    REACTION_TYPES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
        ('heart', 'Heart'),
        ('laugh', 'Laugh'),
        ('wow', 'Wow'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_reactions')
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # User can only have one reaction type per thread
            models.UniqueConstraint(
                fields=['user', 'thread', 'reaction_type'],
                condition=models.Q(thread__isnull=False),
                name='unique_user_thread_reaction'
            ),
            # User can only have one reaction type per post
            models.UniqueConstraint(
                fields=['user', 'post', 'reaction_type'],
                condition=models.Q(post__isnull=False),
                name='unique_user_post_reaction'
            ),
            # Must have either thread or post, not both
            models.CheckConstraint(
                check=(
                    models.Q(thread__isnull=False, post__isnull=True) |
                    models.Q(thread__isnull=True, post__isnull=False)
                ),
                name='reaction_thread_or_post'
            )
        ]

    def __str__(self):
        target = self.thread.title if self.thread else f"post in {self.post.thread.title}"
        return f"{self.user.username} {self.reaction_type} on {target}"
