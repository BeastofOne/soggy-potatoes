from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class AdminSetupProfile(models.Model):
    """Tracks whether admin users have completed the setup wizard."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='setup_profile')
    setup_completed = models.BooleanField(default=False)
    setup_completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Setup {'Complete' if self.setup_completed else 'Pending'}"


class SetupWizardResponse(models.Model):
    """Stores responses from the setup wizard."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='setup_responses')
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Store info
    store_name = models.CharField(max_length=200, blank=True)
    store_tagline = models.CharField(max_length=300, blank=True)
    store_email = models.EmailField(blank=True)

    # Business info
    business_name = models.CharField(max_length=200, blank=True)
    business_address = models.TextField(blank=True)

    # Stripe info (just notes - actual keys go in env vars)
    has_stripe_account = models.BooleanField(default=False)
    stripe_account_email = models.EmailField(blank=True)
    stripe_public_key = models.CharField(max_length=200, blank=True)
    stripe_secret_key = models.CharField(max_length=200, blank=True)

    # Shipping info
    ships_internationally = models.BooleanField(default=False)
    domestic_shipping_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    international_shipping_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    free_shipping_threshold = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Product info
    product_categories = models.TextField(blank=True, help_text="Comma-separated list of categories")
    estimated_product_count = models.CharField(max_length=50, blank=True)
    price_range_low = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_range_high = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Social media
    instagram_handle = models.CharField(max_length=100, blank=True)
    tiktok_handle = models.CharField(max_length=100, blank=True)
    etsy_store_url = models.URLField(blank=True)
    other_social = models.TextField(blank=True)

    # Preferences
    enable_reviews = models.BooleanField(default=True)
    enable_wishlist = models.BooleanField(default=True)
    enable_forum = models.BooleanField(default=True)

    # Additional notes
    questions_for_developer = models.TextField(blank=True)
    additional_features_wanted = models.TextField(blank=True)

    # Email notification sent
    notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Setup by {self.user.username} on {self.submitted_at}"

    def to_email_text(self):
        """Format the response for email/copy-paste."""
        return f"""
========================================
SOGGY POTATOES SETUP WIZARD RESPONSE
Submitted by: {self.user.username}
Date: {self.submitted_at}
========================================

STORE INFORMATION
-----------------
Store Name: {self.store_name}
Tagline: {self.store_tagline}
Contact Email: {self.store_email}

BUSINESS INFORMATION
--------------------
Business Name: {self.business_name}
Address: {self.business_address}

STRIPE PAYMENT SETUP
--------------------
Has Stripe Account: {'Yes' if self.has_stripe_account else 'No'}
Stripe Account Email: {self.stripe_account_email}
Stripe Public Key: {self.stripe_public_key}
Stripe Secret Key: {self.stripe_secret_key}

SHIPPING SETTINGS
-----------------
Ships Internationally: {'Yes' if self.ships_internationally else 'No'}
Domestic Shipping Price: ${self.domestic_shipping_price or 'Not set'}
International Shipping Price: ${self.international_shipping_price or 'Not set'}
Free Shipping Threshold: ${self.free_shipping_threshold or 'Not set'}

PRODUCT INFORMATION
-------------------
Categories to Create: {self.product_categories}
Estimated Number of Products: {self.estimated_product_count}
Price Range: ${self.price_range_low or '?'} - ${self.price_range_high or '?'}

SOCIAL MEDIA
------------
Instagram: {self.instagram_handle}
TikTok: {self.tiktok_handle}
Etsy Store: {self.etsy_store_url}
Other: {self.other_social}

FEATURE PREFERENCES
-------------------
Enable Product Reviews: {'Yes' if self.enable_reviews else 'No'}
Enable Wishlist: {'Yes' if self.enable_wishlist else 'No'}
Enable Community Forum: {'Yes' if self.enable_forum else 'No'}

QUESTIONS FOR DEVELOPER
-----------------------
{self.questions_for_developer or 'None'}

ADDITIONAL FEATURES WANTED
--------------------------
{self.additional_features_wanted or 'None'}

========================================
END OF SETUP RESPONSE
========================================
"""


class Category(models.Model):
    """Product category for organizing stickers."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category', kwargs={'slug': self.slug})


class Product(models.Model):
    """Sticker product."""
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    additional_images = models.JSONField(default=list, blank=True)  # Store additional image paths
    stock = models.PositiveIntegerField(default=0)
    track_inventory = models.BooleanField(default=False, help_text="If disabled, product is always shown as in stock")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        """Return sale price if available, otherwise regular price."""
        if self.sale_price:
            return self.sale_price
        return self.price

    @property
    def is_on_sale(self):
        """Check if product is on sale."""
        return self.sale_price is not None and self.sale_price < self.price

    @property
    def in_stock(self):
        """Check if product is in stock.

        If track_inventory is False (default), product is always in stock.
        If track_inventory is True, checks actual stock count.
        """
        if not self.track_inventory:
            return True  # Always available unless inventory tracking is enabled
        return self.stock > 0

    @property
    def discount_percent(self):
        """Calculate discount percentage."""
        if self.is_on_sale:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0

    @property
    def average_rating(self):
        """Calculate average review rating."""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

    @property
    def review_count(self):
        """Count approved reviews."""
        return self.reviews.filter(is_approved=True).count()


class Cart(models.Model):
    """Shopping cart."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(session_key__isnull=False),
                name='cart_user_or_session'
            )
        ]

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart (session: {self.session_key[:8]}...)"

    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """Calculate cart subtotal."""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Item in shopping cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        """Calculate total price for this item."""
        return self.product.current_price * self.quantity


class Wishlist(models.Model):
    """User's wishlist of products."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlisted_by', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist for {self.user.username}"

    @property
    def count(self):
        return self.products.count()


class Review(models.Model):
    """Product review from customers."""
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=100)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)  # For moderation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']  # One review per user per product
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s review of {self.product.name}"


class Order(models.Model):
    """Customer order."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Shipping info
    shipping_name = models.CharField(max_length=100)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='United States')

    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: SP-YYYYMMDD-XXXX
            import random
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices('0123456789', k=4))
            self.order_number = f"SP-{date_str}-{random_str}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Item in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # Store name in case product deleted
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def total_price(self):
        return self.product_price * self.quantity
