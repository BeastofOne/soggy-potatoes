from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth.decorators import login_required

from .models import Product, Category, Cart, CartItem, Wishlist, Review, Order, OrderItem, AdminSetupProfile, SetupWizardResponse
from .forms import CheckoutForm
from . import payments
from decimal import Decimal
from django.utils import timezone
import stripe
import json
import logging

logger = logging.getLogger(__name__)


# ============================================
# SETUP WIZARD VIEWS
# ============================================

def check_setup_required(user):
    """Check if user needs to complete setup wizard."""
    if not user.is_superuser:
        return False
    try:
        profile = user.setup_profile
        return not profile.setup_completed
    except AdminSetupProfile.DoesNotExist:
        # Create profile for superuser
        AdminSetupProfile.objects.create(user=user)
        return True


@login_required
def setup_wizard(request):
    """Display and handle the setup wizard for superusers."""
    if not request.user.is_superuser:
        return redirect('shop:home')

    # Check if already completed
    try:
        profile = request.user.setup_profile
        if profile.setup_completed:
            return redirect('shop:home')
    except AdminSetupProfile.DoesNotExist:
        profile = AdminSetupProfile.objects.create(user=request.user)

    if request.method == 'POST':
        # Save all the responses
        response = SetupWizardResponse.objects.create(
            user=request.user,
            store_name=request.POST.get('store_name', ''),
            store_tagline=request.POST.get('store_tagline', ''),
            store_email=request.POST.get('store_email', ''),
            business_name=request.POST.get('business_name', ''),
            business_address=request.POST.get('business_address', ''),
            has_stripe_account=request.POST.get('has_stripe_account') == 'true',
            stripe_account_email=request.POST.get('stripe_account_email', ''),
            stripe_public_key=request.POST.get('stripe_public_key', ''),
            stripe_secret_key=request.POST.get('stripe_secret_key', ''),
            ships_internationally=request.POST.get('ships_internationally') == 'true',
            domestic_shipping_price=request.POST.get('domestic_shipping_price') or None,
            international_shipping_price=request.POST.get('international_shipping_price') or None,
            free_shipping_threshold=request.POST.get('free_shipping_threshold') or None,
            product_categories=request.POST.get('product_categories', ''),
            estimated_product_count=request.POST.get('estimated_product_count', ''),
            price_range_low=request.POST.get('price_range_low') or None,
            price_range_high=request.POST.get('price_range_high') or None,
            instagram_handle=request.POST.get('instagram_handle', ''),
            tiktok_handle=request.POST.get('tiktok_handle', ''),
            etsy_store_url=request.POST.get('etsy_store_url', ''),
            other_social=request.POST.get('other_social', ''),
            enable_reviews=request.POST.get('enable_reviews') == 'true',
            enable_wishlist=request.POST.get('enable_wishlist') == 'true',
            enable_forum=request.POST.get('enable_forum') == 'true',
            questions_for_developer=request.POST.get('questions_for_developer', ''),
            additional_features_wanted=request.POST.get('additional_features_wanted', ''),
        )

        # Mark setup as complete
        profile.setup_completed = True
        profile.setup_completed_at = timezone.now()
        profile.save()

        # Try to send email to Jake
        try:
            send_mail(
                subject=f'Soggy Potatoes Setup Completed by {request.user.username}',
                message=response.to_email_text(),
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@soggypotatoes.com',
                recipient_list=['jacob@resourcerealtygroupmi.com'],
                fail_silently=True,
            )
            response.notification_sent = True
            response.save()
        except Exception as e:
            logger.error(f'Failed to send setup notification email: {e}')

        # Redirect to completion page with response text
        return render(request, 'shop/setup/complete.html', {
            'response_text': response.to_email_text()
        })

    return render(request, 'shop/setup/wizard.html')


@login_required
def skip_setup(request):
    """Allow user to skip setup wizard."""
    if not request.user.is_superuser:
        return redirect('shop:home')

    try:
        profile = request.user.setup_profile
    except AdminSetupProfile.DoesNotExist:
        profile = AdminSetupProfile.objects.create(user=request.user)

    profile.setup_completed = True
    profile.setup_completed_at = timezone.now()
    profile.save()

    messages.info(request, 'Setup skipped. You can always run the setup wizard later from the admin panel.')
    return redirect('admin:index')


@login_required
def setup_wizard_edit(request):
    """Edit setup wizard - allows superusers to update their setup anytime."""
    if not request.user.is_superuser:
        return redirect('shop:home')

    # Get the most recent setup response (if any) to pre-fill
    previous_response = SetupWizardResponse.objects.filter(user=request.user).order_by('-submitted_at').first()

    if request.method == 'POST':
        # Save all the responses (creates new record each time for history)
        response = SetupWizardResponse.objects.create(
            user=request.user,
            store_name=request.POST.get('store_name', ''),
            store_tagline=request.POST.get('store_tagline', ''),
            store_email=request.POST.get('store_email', ''),
            business_name=request.POST.get('business_name', ''),
            business_address=request.POST.get('business_address', ''),
            has_stripe_account=request.POST.get('has_stripe_account') == 'true',
            stripe_account_email=request.POST.get('stripe_account_email', ''),
            stripe_public_key=request.POST.get('stripe_public_key', ''),
            stripe_secret_key=request.POST.get('stripe_secret_key', ''),
            ships_internationally=request.POST.get('ships_internationally') == 'true',
            domestic_shipping_price=request.POST.get('domestic_shipping_price') or None,
            international_shipping_price=request.POST.get('international_shipping_price') or None,
            free_shipping_threshold=request.POST.get('free_shipping_threshold') or None,
            product_categories=request.POST.get('product_categories', ''),
            estimated_product_count=request.POST.get('estimated_product_count', ''),
            price_range_low=request.POST.get('price_range_low') or None,
            price_range_high=request.POST.get('price_range_high') or None,
            instagram_handle=request.POST.get('instagram_handle', ''),
            tiktok_handle=request.POST.get('tiktok_handle', ''),
            etsy_store_url=request.POST.get('etsy_store_url', ''),
            other_social=request.POST.get('other_social', ''),
            enable_reviews=request.POST.get('enable_reviews') == 'true',
            enable_wishlist=request.POST.get('enable_wishlist') == 'true',
            enable_forum=request.POST.get('enable_forum') == 'true',
            questions_for_developer=request.POST.get('questions_for_developer', ''),
            additional_features_wanted=request.POST.get('additional_features_wanted', ''),
        )

        # Try to send email to Jake
        try:
            send_mail(
                subject=f'Soggy Potatoes Setup UPDATED by {request.user.username}',
                message=response.to_email_text(),
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@soggypotatoes.com',
                recipient_list=['jacob@resourcerealtygroupmi.com'],
                fail_silently=True,
            )
            response.notification_sent = True
            response.save()
        except Exception as e:
            logger.error(f'Failed to send setup notification email: {e}')

        messages.success(request, 'Setup updated! Jake will be notified of your changes.')
        return render(request, 'shop/setup/complete.html', {
            'response_text': response.to_email_text(),
            'is_update': True
        })

    return render(request, 'shop/setup/wizard_edit.html', {
        'previous': previous_response
    })


class HomeView(TemplateView):
    """Homepage with featured products and welcome message."""
    template_name = 'shop/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Welcome'
        context['featured_products'] = Product.objects.filter(
            is_featured=True,
            is_active=True
        )[:6]
        context['categories'] = Category.objects.filter(is_active=True)
        return context


class AboutView(TemplateView):
    """About page for Joana."""
    template_name = 'shop/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'About'
        return context


class ProductListView(ListView):
    """List all products with optional filtering."""
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Sort options
        sort = self.request.GET.get('sort', '-created_at')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_sort'] = self.request.GET.get('sort', '-created_at')

        # Get current category if filtering
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)

        return context


class ProductDetailView(DetailView):
    """Product detail page."""
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related products from same category
        if self.object.category:
            context['related_products'] = Product.objects.filter(
                category=self.object.category,
                is_active=True
            ).exclude(pk=self.object.pk)[:4]

        # Get reviews
        context['reviews'] = self.object.reviews.filter(is_approved=True)

        # Check if user can review (logged in and hasn't reviewed yet)
        if self.request.user.is_authenticated:
            context['can_review'] = not Review.objects.filter(
                product=self.object,
                user=self.request.user
            ).exists()
            # Check if product is in user's wishlist
            try:
                wishlist = self.request.user.wishlist
                context['in_wishlist'] = wishlist.products.filter(pk=self.object.pk).exists()
            except Wishlist.DoesNotExist:
                context['in_wishlist'] = False
        else:
            context['can_review'] = False
            context['in_wishlist'] = False

        return context


class ProductSearchView(ListView):
    """Search products."""
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query),
                is_active=True
            )
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.filter(is_active=True)
        return context


# Cart helper functions
def get_or_create_cart(request):
    """Get or create a cart for the current user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_view(request):
    """Display shopping cart."""
    cart = get_or_create_cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})


@require_POST
@csrf_protect
def add_to_cart(request, product_id):
    """Add a product to the cart."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    # Check stock
    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available.')
        return redirect('shop:product_detail', slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, f'Sorry, only {product.stock} items available.')
            return redirect('shop:product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
        cart_item.save()

    messages.success(request, f'Added {product.name} to your cart!')

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_items,
            'message': f'Added {product.name} to your cart!'
        })

    return redirect('shop:cart')


@require_POST
@csrf_protect
def update_cart(request, item_id):
    """Update cart item quantity."""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Item removed from cart.')
    elif quantity > cart_item.product.stock:
        messages.error(request, f'Sorry, only {cart_item.product.stock} items available.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')

    return redirect('shop:cart')


@require_POST
@csrf_protect
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f'Removed {product_name} from your cart.')

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.total_items,
            'subtotal': str(cart.subtotal)
        })

    return redirect('shop:cart')


# Wishlist views
@login_required
def wishlist_view(request):
    """Display user's wishlist."""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'shop/wishlist.html', {'wishlist': wishlist})


@login_required
@require_POST
@csrf_protect
def toggle_wishlist(request, product_id):
    """Add or remove product from wishlist."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(pk=product_id).exists():
        wishlist.products.remove(product)
        action = 'removed'
        messages.info(request, f'{product.name} removed from your wishlist.')
    else:
        wishlist.products.add(product)
        action = 'added'
        messages.success(request, f'{product.name} added to your wishlist!')

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'wishlist_count': wishlist.count
        })

    # Redirect back to where user came from
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'shop:product_list'))
    return redirect(next_url)


# Review views
@login_required
@require_POST
@csrf_protect
def add_review(request, product_id):
    """Add a review for a product."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    # Check if user already reviewed
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'You have already reviewed this product.')
        return redirect('shop:product_detail', slug=product.slug)

    rating = int(request.POST.get('rating', 5))
    title = request.POST.get('title', '')
    comment = request.POST.get('comment', '')

    if not title or not comment:
        messages.error(request, 'Please provide both a title and comment for your review.')
        return redirect('shop:product_detail', slug=product.slug)

    # Check if user has purchased this product (verified purchase)
    is_verified = Order.objects.filter(
        user=request.user,
        items__product=product,
        status__in=['delivered', 'shipped']
    ).exists()

    Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        title=title,
        comment=comment,
        is_verified_purchase=is_verified
    )

    messages.success(request, 'Thank you for your review!')
    return redirect('shop:product_detail', slug=product.slug)


# Order history view
@login_required
def order_history(request):
    """Display user's order history."""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    """Display order details."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


# Checkout views
@login_required
def checkout_view(request):
    """Display checkout page with shipping form."""
    cart = get_or_create_cart(request)

    # Check if cart is empty
    if cart.total_items == 0:
        messages.warning(request, 'Your cart is empty. Add some stickers before checkout!')
        return redirect('shop:product_list')

    # Check stock for all items
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(
                request,
                f'Sorry, only {item.product.stock} of "{item.product.name}" available. Please update your cart.'
            )
            return redirect('shop:cart')

    # Calculate totals
    subtotal = cart.subtotal
    shipping_cost = Decimal('0.00')  # Free shipping for now
    tax = Decimal('0.00')  # No tax calculation yet
    total = subtotal + shipping_cost + tax

    # Pre-fill form with user info if available
    initial_data = {
        'email': request.user.email,
        'shipping_name': f'{request.user.first_name} {request.user.last_name}'.strip() or request.user.username,
    }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order with pending status
            order = Order.objects.create(
                user=request.user,
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                shipping_name=form.cleaned_data['shipping_name'],
                shipping_address=form.cleaned_data['shipping_address'],
                shipping_city=form.cleaned_data['shipping_city'],
                shipping_state=form.cleaned_data['shipping_state'],
                shipping_zip=form.cleaned_data['shipping_zip'],
                shipping_country=form.cleaned_data['shipping_country'],
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax=tax,
                total=total,
                status='pending',
            )

            # Create order items (don't reduce stock yet - wait for payment)
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_price=cart_item.product.current_price,
                    quantity=cart_item.quantity,
                )

            # Store order ID in session for later reference
            request.session['pending_order_id'] = order.id

            # Check if Stripe keys are configured
            if settings.STRIPE_SECRET_KEY and not settings.STRIPE_SECRET_KEY.startswith('pk_test_placeholder'):
                # Create Stripe Checkout Session
                try:
                    success_url = request.build_absolute_uri(
                        reverse('shop:payment_success') + '?session_id={CHECKOUT_SESSION_ID}'
                    )
                    cancel_url = request.build_absolute_uri(
                        reverse('shop:payment_cancelled')
                    )

                    session = payments.create_checkout_session(
                        request, order, success_url, cancel_url
                    )

                    # Store session ID in order
                    order.stripe_payment_intent_id = session.id
                    order.save()

                    # Redirect to Stripe Checkout
                    return redirect(session.url)

                except stripe.error.StripeError as e:
                    logger.error(f'Stripe error: {e}')
                    messages.error(request, 'Payment processing error. Please try again.')
                    order.delete()
                    return redirect('shop:checkout')
            else:
                # Development mode - skip payment, mark as paid
                order.status = 'processing'
                order.save()

                # Reduce stock
                for cart_item in cart.items.all():
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()

                # Clear cart
                cart.items.all().delete()

                # Send confirmation email
                send_order_confirmation_email(order)

                messages.success(request, f'Order {order.order_number} placed successfully! (Dev mode - payment skipped)')
                return redirect('shop:order_confirmation', order_number=order.order_number)
    else:
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'total': total,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def payment_success(request):
    """Handle successful Stripe payment redirect."""
    session_id = request.GET.get('session_id')

    if not session_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('shop:home')

    try:
        # Retrieve session from Stripe
        session = payments.retrieve_checkout_session(session_id)

        # Find the order
        order = Order.objects.get(stripe_payment_intent_id=session_id)

        # Verify payment was successful
        if session.payment_status == 'paid':
            # Update order status
            order.status = 'processing'
            order.save()

            # Reduce stock
            for item in order.items.all():
                if item.product:
                    item.product.stock -= item.quantity
                    item.product.save()

            # Clear cart
            cart = get_or_create_cart(request)
            cart.items.all().delete()

            # Clear session
            if 'pending_order_id' in request.session:
                del request.session['pending_order_id']

            # Send confirmation email
            send_order_confirmation_email(order)

            messages.success(request, f'Payment successful! Order {order.order_number} confirmed.')
            return redirect('shop:order_confirmation', order_number=order.order_number)
        else:
            messages.warning(request, 'Payment is being processed. You will receive a confirmation email shortly.')
            return redirect('shop:order_detail', order_number=order.order_number)

    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('shop:home')
    except stripe.error.StripeError as e:
        logger.error(f'Stripe error retrieving session: {e}')
        messages.error(request, 'Error verifying payment. Please contact support.')
        return redirect('shop:home')


@login_required
def payment_cancelled(request):
    """Handle cancelled Stripe payment."""
    pending_order_id = request.session.get('pending_order_id')

    if pending_order_id:
        try:
            order = Order.objects.get(id=pending_order_id, user=request.user, status='pending')
            # Delete the pending order since payment was cancelled
            order.delete()
            del request.session['pending_order_id']
        except Order.DoesNotExist:
            pass

    messages.info(request, 'Payment cancelled. Your cart items are still saved.')
    return redirect('shop:cart')


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        return HttpResponse(status=400)

    try:
        event = payments.construct_webhook_event(payload, sig_header)
    except ValueError:
        # Invalid payload
        logger.error('Invalid Stripe webhook payload')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        logger.error('Invalid Stripe webhook signature')
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session)
    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        handle_failed_payment(intent)

    return HttpResponse(status=200)


def handle_successful_payment(session):
    """Process successful payment from webhook."""
    try:
        order = Order.objects.get(stripe_payment_intent_id=session['id'])

        if order.status == 'pending':
            order.status = 'processing'
            order.save()

            # Reduce stock
            for item in order.items.all():
                if item.product:
                    item.product.stock -= item.quantity
                    item.product.save()

            # Send confirmation email
            send_order_confirmation_email(order)

            logger.info(f'Order {order.order_number} payment confirmed via webhook')

    except Order.DoesNotExist:
        logger.error(f'Order not found for session {session["id"]}')


def handle_failed_payment(intent):
    """Process failed payment from webhook."""
    try:
        order = Order.objects.get(stripe_payment_intent_id=intent['id'])
        order.status = 'cancelled'
        order.save()
        logger.info(f'Order {order.order_number} payment failed')
    except Order.DoesNotExist:
        logger.error(f'Order not found for intent {intent["id"]}')


def send_order_confirmation_email(order):
    """Send order confirmation email to customer."""
    subject = f'Order Confirmed - {order.order_number} - Soggy Potatoes'

    # Render HTML email
    html_message = render_to_string('shop/emails/order_confirmation.html', {
        'order': order,
    })
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@soggypotatoes.com',
            [order.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f'Order confirmation email sent for {order.order_number}')
    except Exception as e:
        logger.error(f'Failed to send order confirmation email: {e}')


@login_required
def order_confirmation(request, order_number):
    """Display order confirmation page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})
