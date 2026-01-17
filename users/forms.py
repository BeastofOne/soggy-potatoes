from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ReservedUsername


# Reserved patterns that should never be in a username
RESERVED_PATTERNS = [
    'admin', 'administrator', 'owner', 'staff', 'moderator', 'mod',
    'support', 'help', 'official', 'soggy', 'potatoes', 'soggypotatoes',
    'system', 'root', 'superuser', 'webmaster', 'postmaster',
]


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with username validation."""
    email = forms.EmailField(
        required=True,
        help_text="Required. We'll send you a welcome email!"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            return username

        username_lower = username.lower()

        # Check reserved usernames from database
        if ReservedUsername.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is not available.")

        # Check reserved patterns
        for pattern in RESERVED_PATTERNS:
            if pattern in username_lower:
                raise forms.ValidationError(
                    "This username contains reserved words. Please choose another."
                )

        # Check blocked words (profanity filter)
        try:
            from messaging.filters import check_username_allowed
            is_allowed, reason = check_username_allowed(username)
            if not is_allowed:
                raise forms.ValidationError(reason)
        except ImportError:
            pass  # Messaging app not installed yet

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
