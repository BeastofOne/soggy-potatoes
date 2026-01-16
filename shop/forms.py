from django import forms
from .models import Order


class CheckoutForm(forms.Form):
    """Form for checkout shipping and contact information."""

    # Contact Information
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(555) 123-4567'
        })
    )

    # Shipping Information
    shipping_name = forms.CharField(
        max_length=100,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John Doe'
        })
    )
    shipping_address = forms.CharField(
        label='Street Address',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': '123 Main St\nApt 4B',
            'rows': 2
        })
    )
    shipping_city = forms.CharField(
        max_length=100,
        label='City',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'New York'
        })
    )
    shipping_state = forms.CharField(
        max_length=100,
        label='State / Province',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'NY'
        })
    )
    shipping_zip = forms.CharField(
        max_length=20,
        label='ZIP / Postal Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10001'
        })
    )
    shipping_country = forms.ChoiceField(
        label='Country',
        choices=[
            ('United States', 'United States'),
            ('Canada', 'Canada'),
            ('United Kingdom', 'United Kingdom'),
            ('Australia', 'Australia'),
            ('Germany', 'Germany'),
            ('France', 'France'),
            ('Japan', 'Japan'),
            ('Other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def clean_shipping_zip(self):
        """Validate ZIP code format."""
        zip_code = self.cleaned_data.get('shipping_zip', '')
        # Remove spaces and dashes for validation
        cleaned_zip = zip_code.replace(' ', '').replace('-', '')
        if len(cleaned_zip) < 3:
            raise forms.ValidationError('Please enter a valid ZIP/postal code.')
        return zip_code

    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('email', '')
        if not email:
            raise forms.ValidationError('Email is required for order confirmation.')
        return email.lower()
