from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.db.models import Count

from .models import ForumCategory, Thread, Post, Reaction


class ForumHomeView(ListView):
    """Forum homepage showing all categories."""
    model = ForumCategory
    template_name = 'forum/home.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return ForumCategory.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_threads'] = Thread.objects.select_related(
            'author', 'category'
        ).order_by('-created_at')[:5]
        context['popular_threads'] = Thread.objects.annotate(
            reaction_count=Count('reactions')
        ).order_by('-reaction_count', '-views')[:5]
        return context


class CategoryDetailView(ListView):
    """Show threads in a category."""
    model = Thread
    template_name = 'forum/category.html'
    context_object_name = 'threads'
    paginate_by = 20

    def get_queryset(self):
        self.category = get_object_or_404(ForumCategory, slug=self.kwargs['slug'], is_active=True)
        return Thread.objects.filter(category=self.category).select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ThreadDetailView(DetailView):
    """Show thread with all posts."""
    model = Thread
    template_name = 'forum/thread.html'
    context_object_name = 'thread'

    def get_object(self):
        thread = get_object_or_404(
            Thread,
            category__slug=self.kwargs['category_slug'],
            slug=self.kwargs['thread_slug']
        )
        # Increment view count
        thread.views += 1
        thread.save(update_fields=['views'])
        return thread

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.select_related('author').all()

        # Check user's reactions if logged in
        if self.request.user.is_authenticated:
            user_reactions = Reaction.objects.filter(
                user=self.request.user,
                thread=self.object
            ).values_list('reaction_type', flat=True)
            context['user_thread_reactions'] = list(user_reactions)

            # Get user's reactions on posts
            post_reactions = Reaction.objects.filter(
                user=self.request.user,
                post__in=self.object.posts.all()
            ).values('post_id', 'reaction_type')
            context['user_post_reactions'] = {
                r['post_id']: r['reaction_type'] for r in post_reactions
            }
        else:
            context['user_thread_reactions'] = []
            context['user_post_reactions'] = {}

        return context


class CreateThreadView(LoginRequiredMixin, CreateView):
    """Create a new thread."""
    model = Thread
    template_name = 'forum/create_thread.html'
    fields = ['title', 'content']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(ForumCategory, slug=self.kwargs['category_slug'])
        return context

    def form_valid(self, form):
        category = get_object_or_404(ForumCategory, slug=self.kwargs['category_slug'])
        form.instance.category = category
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # Create the first post (thread content)
        Post.objects.create(
            thread=self.object,
            author=self.request.user,
            content=form.cleaned_data['content']
        )

        messages.success(self.request, 'Thread created successfully!')
        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


@login_required
@require_POST
@csrf_protect
def create_reply(request, category_slug, thread_slug):
    """Create a reply to a thread."""
    thread = get_object_or_404(Thread, category__slug=category_slug, slug=thread_slug)

    if thread.is_locked:
        messages.error(request, 'This thread is locked and cannot receive new replies.')
        return redirect(thread.get_absolute_url())

    content = request.POST.get('content', '').strip()
    if not content:
        messages.error(request, 'Reply content cannot be empty.')
        return redirect(thread.get_absolute_url())

    Post.objects.create(
        thread=thread,
        author=request.user,
        content=content
    )

    messages.success(request, 'Reply posted successfully!')
    return redirect(thread.get_absolute_url())


@login_required
@require_POST
@csrf_protect
def toggle_reaction(request):
    """Toggle a reaction on a thread or post."""
    reaction_type = request.POST.get('reaction_type', 'upvote')
    thread_id = request.POST.get('thread_id')
    post_id = request.POST.get('post_id')

    if not thread_id and not post_id:
        return JsonResponse({'error': 'Must specify thread or post'}, status=400)

    if thread_id:
        thread = get_object_or_404(Thread, pk=thread_id)
        existing = Reaction.objects.filter(
            user=request.user,
            thread=thread,
            reaction_type=reaction_type
        ).first()

        if existing:
            existing.delete()
            action = 'removed'
        else:
            # Remove opposite reaction if exists (for upvote/downvote)
            if reaction_type in ['upvote', 'downvote']:
                opposite = 'downvote' if reaction_type == 'upvote' else 'upvote'
                Reaction.objects.filter(
                    user=request.user,
                    thread=thread,
                    reaction_type=opposite
                ).delete()

            Reaction.objects.create(
                user=request.user,
                thread=thread,
                reaction_type=reaction_type
            )
            action = 'added'

        return JsonResponse({
            'success': True,
            'action': action,
            'upvotes': thread.upvote_count,
            'downvotes': thread.downvote_count,
            'score': thread.score
        })

    if post_id:
        post = get_object_or_404(Post, pk=post_id)
        existing = Reaction.objects.filter(
            user=request.user,
            post=post,
            reaction_type=reaction_type
        ).first()

        if existing:
            existing.delete()
            action = 'removed'
        else:
            # Remove opposite reaction if exists
            if reaction_type in ['upvote', 'downvote']:
                opposite = 'downvote' if reaction_type == 'upvote' else 'upvote'
                Reaction.objects.filter(
                    user=request.user,
                    post=post,
                    reaction_type=opposite
                ).delete()

            Reaction.objects.create(
                user=request.user,
                post=post,
                reaction_type=reaction_type
            )
            action = 'added'

        return JsonResponse({
            'success': True,
            'action': action,
            'upvotes': post.upvote_count,
            'downvotes': post.downvote_count,
            'score': post.score
        })
