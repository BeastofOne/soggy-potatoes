from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib import messages
from .models import AdminSetupProfile


class BannedUserMiddleware:
    """
    Middleware to prevent banned users from accessing the site.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if user is banned
            if hasattr(request.user, 'ban') and request.user.ban.is_active:
                reason = request.user.ban.reason
                logout(request)
                messages.error(request, f'Your account has been suspended. Reason: {reason}')
                return redirect('users:login')

        return self.get_response(request)


class SetupWizardMiddleware:
    """
    Middleware to redirect superusers to setup wizard on first login.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that should be accessible without completing setup
        self.exempt_urls = [
            '/setup/',
            '/setup/skip/',
            '/admin/logout/',
            '/accounts/logout/',
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        # Skip for non-authenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip for non-superusers
        if not request.user.is_superuser:
            return self.get_response(request)

        # Skip for exempt URLs
        path = request.path
        if any(path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)

        # Check if setup is required
        try:
            profile = request.user.setup_profile
            if not profile.setup_completed:
                return redirect('shop:setup_wizard')
        except AdminSetupProfile.DoesNotExist:
            # Create profile and redirect to wizard
            AdminSetupProfile.objects.create(user=request.user)
            return redirect('shop:setup_wizard')

        return self.get_response(request)
