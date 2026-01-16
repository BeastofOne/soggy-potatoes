from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import Product, Category, Cart, CartItem


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
