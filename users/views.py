from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.paginator import Paginator

from .models import UserProfile, PetPhoto, Badge, UserBadge, UserBan, PostReport
from .forms import CustomUserCreationForm


def superuser_required(view_func):
    """Decorator that requires the user to be a superuser."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("Access denied. Superuser privileges required.")
        return view_func(request, *args, **kwargs)
    return wrapper


class RegisterView(CreateView):
    """User registration view."""
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Check your email for a welcome message.')
        return response

    def dispatch(self, request, *args, **kwargs):
        # Redirect to home if already logged in
        if request.user.is_authenticated:
            return redirect('shop:home')
        return super().dispatch(request, *args, **kwargs)


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect to 'next' parameter or home
            next_url = request.GET.get('next', 'shop:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('shop:home')


@login_required
def profile_view(request):
    """User profile view (private dashboard)."""
    from shop.models import Order, Review

    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'profile': profile,
        'recent_orders': Order.objects.filter(user=request.user)[:5],
        'recent_reviews': Review.objects.filter(user=request.user)[:5],
    }
    return render(request, 'users/profile.html', context)


def public_profile_view(request, username):
    """View another user's public profile."""
    from shop.models import Review
    from forum.models import Thread, Post

    profile_user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=profile_user)

    # Get user's forum activity
    threads = Thread.objects.filter(author=profile_user).order_by('-created_at')[:5]
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')[:10]
    reviews = Review.objects.filter(user=profile_user).order_by('-created_at')[:5]

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'threads': threads,
        'posts': posts,
        'reviews': reviews,
        'pet_photos': profile.pet_photos.all()[:6],
        'is_own_profile': request.user == profile_user,
    }
    return render(request, 'users/public_profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit your own profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update profile fields
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.website = request.POST.get('website', '')
        profile.has_pets = request.POST.get('has_pets') == 'on'
        profile.pet_count = int(request.POST.get('pet_count', 0) or 0)
        profile.pet_names = request.POST.get('pet_names', '')
        profile.pet_types = request.POST.get('pet_types', '')
        profile.favorite_pet_story = request.POST.get('favorite_pet_story', '')

        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()

        # Handle pet photo uploads
        pet_photos = request.FILES.getlist('pet_photos')
        for photo in pet_photos[:6]:  # Limit to 6 photos at a time
            caption = request.POST.get('photo_caption', '')
            PetPhoto.objects.create(
                profile=profile,
                image=photo,
                caption=caption
            )

        messages.success(request, 'Profile updated successfully!')
        return redirect('users:public_profile', username=request.user.username)

    context = {
        'profile': profile,
        'pet_photos': profile.pet_photos.all(),
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
def delete_pet_photo(request, photo_id):
    """Delete a pet photo."""
    photo = get_object_or_404(PetPhoto, pk=photo_id, profile__user=request.user)
    photo.delete()
    messages.success(request, 'Photo deleted.')
    return redirect('users:edit_profile')


# =============================================
# SUPERUSER ADMIN DASHBOARD VIEWS
# =============================================

@login_required
@superuser_required
def admin_dashboard(request):
    """Admin dashboard for superusers - easy management interface."""
    from shop.models import Product, Category, Order
    from forum.models import Thread, Post

    context = {
        'products': Product.objects.all().order_by('-created_at')[:10],
        'product_count': Product.objects.count(),
        'category_count': Category.objects.count(),
        'order_count': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'user_count': User.objects.count(),
        'badges': Badge.objects.all(),
        'pending_reports': PostReport.objects.filter(status='pending').count(),
        'recent_reports': PostReport.objects.filter(status='pending')[:5],
        'banned_users': UserBan.objects.all()[:10],
    }
    return render(request, 'users/admin/dashboard.html', context)


@login_required
@superuser_required
def admin_products(request):
    """Manage products - list, edit, delete."""
    from shop.models import Product, Category

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            # Create new product
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            price = request.POST.get('price')
            stock = request.POST.get('stock', 0)
            track_inventory = request.POST.get('track_inventory') == 'on'
            category_id = request.POST.get('category')
            is_active = request.POST.get('is_active') == 'on'
            is_featured = request.POST.get('is_featured') == 'on'

            product = Product(
                name=name,
                description=description,
                price=price,
                stock=int(stock) if stock else 0,
                track_inventory=track_inventory,
                is_active=is_active,
                is_featured=is_featured
            )
            if category_id:
                product.category = Category.objects.get(pk=category_id)
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            product.save()
            messages.success(request, f'Product "{name}" created successfully!')

        elif action == 'update':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, pk=product_id)
            product.name = request.POST.get('name', product.name)
            product.description = request.POST.get('description', product.description)
            product.price = request.POST.get('price', product.price)
            product.stock = int(request.POST.get('stock', product.stock) or 0)
            product.track_inventory = request.POST.get('track_inventory') == 'on'
            product.is_active = request.POST.get('is_active') == 'on'
            product.is_featured = request.POST.get('is_featured') == 'on'

            category_id = request.POST.get('category')
            if category_id:
                product.category = Category.objects.get(pk=category_id)
            else:
                product.category = None

            if 'image' in request.FILES:
                product.image = request.FILES['image']

            # Handle sale price
            sale_price = request.POST.get('sale_price')
            product.sale_price = sale_price if sale_price else None

            product.save()
            messages.success(request, f'Product "{product.name}" updated!')

        elif action == 'delete':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, pk=product_id)
            name = product.name
            product.delete()
            messages.success(request, f'Product "{name}" deleted!')

        return redirect('users:admin_products')

    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'users/admin/products.html', context)


@login_required
@superuser_required
def admin_badges(request):
    """Manage badges - create, delete, award."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            if 'image' in request.FILES:
                Badge.objects.create(
                    name=name,
                    description=description,
                    image=request.FILES['image'],
                    created_by=request.user
                )
                messages.success(request, f'Badge "{name}" created!')
            else:
                messages.error(request, 'Please upload an image for the badge.')

        elif action == 'delete':
            badge_id = request.POST.get('badge_id')
            badge = get_object_or_404(Badge, pk=badge_id)
            name = badge.name
            badge.delete()
            messages.success(request, f'Badge "{name}" deleted!')

        return redirect('users:admin_badges')

    badges = Badge.objects.all()
    context = {'badges': badges}
    return render(request, 'users/admin/badges.html', context)


@login_required
@superuser_required
def award_badge(request, username):
    """Award a badge to a user."""
    user = get_object_or_404(User, username=username)
    badges = Badge.objects.all()

    if request.method == 'POST':
        badge_id = request.POST.get('badge_id')
        badge = get_object_or_404(Badge, pk=badge_id)

        # Check if user already has this badge
        if UserBadge.objects.filter(user=user, badge=badge).exists():
            messages.warning(request, f'{user.username} already has the "{badge.name}" badge.')
        else:
            UserBadge.objects.create(user=user, badge=badge, awarded_by=request.user)
            messages.success(request, f'Awarded "{badge.name}" badge to {user.username}!')

        return redirect('users:public_profile', username=username)

    context = {
        'target_user': user,
        'badges': badges,
        'user_badges': UserBadge.objects.filter(user=user),
    }
    return render(request, 'users/admin/award_badge.html', context)


@login_required
@superuser_required
def remove_badge(request, username, badge_id):
    """Remove a badge from a user."""
    user = get_object_or_404(User, username=username)
    user_badge = get_object_or_404(UserBadge, user=user, badge_id=badge_id)
    badge_name = user_badge.badge.name
    user_badge.delete()
    messages.success(request, f'Removed "{badge_name}" badge from {user.username}.')
    return redirect('users:public_profile', username=username)


@login_required
@superuser_required
def admin_reports(request):
    """View and manage post reports."""
    status_filter = request.GET.get('status', 'pending')

    if status_filter == 'all':
        reports = PostReport.objects.all()
    else:
        reports = PostReport.objects.filter(status=status_filter)

    context = {
        'reports': reports,
        'status_filter': status_filter,
    }
    return render(request, 'users/admin/reports.html', context)


@login_required
@superuser_required
def handle_report(request, report_id):
    """Handle a report - dismiss, take action, etc."""
    report = get_object_or_404(PostReport, pk=report_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('admin_notes', '')

        report.admin_notes = notes
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()

        if action == 'dismiss':
            report.status = 'dismissed'
            messages.info(request, 'Report dismissed.')

        elif action == 'delete_content':
            report.status = 'action_taken'
            # Delete the reported content
            if report.post:
                report.post.delete()
                messages.success(request, 'Post deleted and report resolved.')
            elif report.thread:
                report.thread.delete()
                messages.success(request, 'Thread deleted and report resolved.')

        elif action == 'ban_user':
            report.status = 'action_taken'
            # Get the author of reported content
            if report.post:
                user_to_ban = report.post.author
            else:
                user_to_ban = report.thread.author

            # Create ban (if not already banned)
            if not hasattr(user_to_ban, 'ban'):
                UserBan.objects.create(
                    user=user_to_ban,
                    reason=f"Banned for reported content. Report details: {report.details}",
                    banned_by=request.user
                )
                messages.success(request, f'{user_to_ban.username} has been banned.')
            else:
                messages.warning(request, f'{user_to_ban.username} is already banned.')

        report.save()
        return redirect('users:admin_reports')

    context = {'report': report}
    return render(request, 'users/admin/handle_report.html', context)


@login_required
@superuser_required
def ban_user(request, username):
    """Ban a user."""
    user = get_object_or_404(User, username=username)

    if user.is_superuser:
        messages.error(request, 'Cannot ban a superuser.')
        return redirect('users:public_profile', username=username)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'No reason provided')
        expires = request.POST.get('expires')  # Optional expiration

        # Check if already banned
        if hasattr(user, 'ban'):
            messages.warning(request, f'{user.username} is already banned.')
        else:
            ban = UserBan(user=user, reason=reason, banned_by=request.user)
            if expires:
                ban.expires_at = timezone.datetime.fromisoformat(expires)
            ban.save()
            messages.success(request, f'{user.username} has been banned.')

        return redirect('users:admin_dashboard')

    context = {'target_user': user}
    return render(request, 'users/admin/ban_user.html', context)


@login_required
@superuser_required
def unban_user(request, username):
    """Unban a user."""
    user = get_object_or_404(User, username=username)

    if hasattr(user, 'ban'):
        user.ban.delete()
        messages.success(request, f'{user.username} has been unbanned.')
    else:
        messages.info(request, f'{user.username} is not banned.')

    return redirect('users:admin_dashboard')


@login_required
@superuser_required
def delete_thread(request, thread_id):
    """Delete a forum thread."""
    from forum.models import Thread
    thread = get_object_or_404(Thread, pk=thread_id)
    title = thread.title
    category_slug = thread.category.slug
    thread.delete()
    messages.success(request, f'Thread "{title}" has been deleted.')
    return redirect('forum:category', slug=category_slug)


@login_required
@superuser_required
def delete_post(request, post_id):
    """Delete a forum post."""
    from forum.models import Post
    post = get_object_or_404(Post, pk=post_id)
    thread_url = post.thread.get_absolute_url()
    post.delete()
    messages.success(request, 'Post has been deleted.')
    return redirect(thread_url)


# =============================================
# REPORT POST FUNCTIONALITY (for all users)
# =============================================

@login_required
def report_post(request, post_id):
    """Report a forum post."""
    from forum.models import Post
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        details = request.POST.get('details', '')

        # Create the report
        report = PostReport.objects.create(
            post=post,
            reporter=request.user,
            reason=reason,
            details=details
        )

        # Send email notification to Joana
        try:
            subject = f'New Forum Report - {report.get_reason_display()}'
            html_message = render_to_string('users/emails/report_notification.html', {
                'report': report,
                'post': post,
                'reporter': request.user,
            })
            send_mail(
                subject,
                f"New report on a forum post by {post.author.username}. Reason: {reason}",
                None,  # From (uses DEFAULT_FROM_EMAIL)
                ['kittytherese13@gmail.com'],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception:
            pass  # Don't fail if email doesn't send

        messages.success(request, 'Thank you for your report. Our team will review it.')
        return redirect(post.thread.get_absolute_url())

    context = {'post': post}
    return render(request, 'users/report_post.html', context)


@login_required
def report_thread(request, thread_id):
    """Report a forum thread."""
    from forum.models import Thread
    thread = get_object_or_404(Thread, pk=thread_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        details = request.POST.get('details', '')

        # Create the report
        report = PostReport.objects.create(
            thread=thread,
            reporter=request.user,
            reason=reason,
            details=details
        )

        # Send email notification to Joana
        try:
            subject = f'New Forum Report - {report.get_reason_display()}'
            html_message = render_to_string('users/emails/report_notification.html', {
                'report': report,
                'thread': thread,
                'reporter': request.user,
            })
            send_mail(
                subject,
                f"New report on thread '{thread.title}' by {thread.author.username}. Reason: {reason}",
                None,
                ['kittytherese13@gmail.com'],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, 'Thank you for your report. Our team will review it.')
        return redirect(thread.get_absolute_url())

    context = {'thread': thread}
    return render(request, 'users/report_thread.html', context)


# =============================================
# AJAX ENDPOINTS FOR SUPERUSER ACTIONS
# =============================================

@login_required
def get_user_badges(request, username):
    """Get badges for a user (AJAX)."""
    user = get_object_or_404(User, username=username)
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')

    badges_data = [{
        'id': ub.badge.id,
        'name': ub.badge.name,
        'image_url': ub.badge.image.url if ub.badge.image else '',
        'awarded_at': ub.awarded_at.isoformat(),
    } for ub in user_badges]

    return JsonResponse({'badges': badges_data})
