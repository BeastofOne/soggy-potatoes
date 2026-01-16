from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy

from .models import UserProfile, PetPhoto


class RegisterView(CreateView):
    """User registration view."""
    form_class = UserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please log in.')
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
