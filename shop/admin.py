from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Cart, CartItem, Wishlist, Review, Order, OrderItem, AdminSetupProfile, SetupWizardResponse

# Customize admin site
admin.site.site_header = "Soggy Potatoes Admin"
admin.site.site_title = "Soggy Potatoes"
admin.site.index_title = "Store Management"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'name', 'category', 'price', 'sale_price', 'stock', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'sale_price', 'stock', 'is_active', 'is_featured']
    list_per_page = 20
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Images', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
    )

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return format_html('<span style="color: #999;">No image</span>')
    thumbnail.short_description = 'Image'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key_short', 'total_items', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['total_items', 'subtotal']

    def session_key_short(self, obj):
        if obj.session_key:
            return f"{obj.session_key[:8]}..."
        return "-"
    session_key_short.short_description = 'Session'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_count', 'created_at']
    search_fields = ['user__username']
    filter_horizontal = ['products']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_verified_purchase', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['is_verified_purchase']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total', 'created_at', 'paid_at']
    list_filter = ['status', 'created_at', 'paid_at']
    search_fields = ['order_number', 'user__username', 'email', 'shipping_name']
    readonly_fields = ['order_number', 'subtotal', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    list_editable = ['status']

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Shipping', {
            'fields': ('shipping_name', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip', 'shipping_country')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('Payment', {
            'fields': ('stripe_payment_intent_id', 'paid_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Setup Wizard Admin
@admin.register(AdminSetupProfile)
class AdminSetupProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'setup_completed', 'setup_completed_at', 'created_at']
    list_filter = ['setup_completed']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        return False  # Profiles are created automatically


@admin.register(SetupWizardResponse)
class SetupWizardResponseAdmin(admin.ModelAdmin):
    list_display = ['user', 'store_name', 'has_stripe_account', 'notification_sent', 'submitted_at']
    list_filter = ['has_stripe_account', 'notification_sent', 'submitted_at']
    search_fields = ['user__username', 'store_name', 'store_email']
    readonly_fields = ['submitted_at', 'user']

    fieldsets = (
        ('Submitted By', {
            'fields': ('user', 'submitted_at')
        }),
        ('Store Information', {
            'fields': ('store_name', 'store_tagline', 'store_email')
        }),
        ('Business Information', {
            'fields': ('business_name', 'business_address')
        }),
        ('Stripe Setup', {
            'fields': ('has_stripe_account', 'stripe_account_email', 'stripe_public_key', 'stripe_secret_key'),
            'description': 'IMPORTANT: Copy these keys to environment variables in Render!'
        }),
        ('Shipping', {
            'fields': ('ships_internationally', 'domestic_shipping_price', 'international_shipping_price', 'free_shipping_threshold')
        }),
        ('Products', {
            'fields': ('product_categories', 'estimated_product_count', 'price_range_low', 'price_range_high')
        }),
        ('Social Media', {
            'fields': ('instagram_handle', 'tiktok_handle', 'etsy_store_url', 'other_social')
        }),
        ('Features', {
            'fields': ('enable_reviews', 'enable_wishlist', 'enable_forum')
        }),
        ('Additional', {
            'fields': ('questions_for_developer', 'additional_features_wanted')
        }),
        ('Status', {
            'fields': ('notification_sent',)
        }),
    )

    def has_add_permission(self, request):
        return False  # Responses come from the wizard only
