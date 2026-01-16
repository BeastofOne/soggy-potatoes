from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth.decorators import login_required

from .models import Product, Category, Cart, CartItem, Wishlist, Review, Order


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
