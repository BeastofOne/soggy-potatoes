from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Setup wizard (for first-time superusers)
    path('setup/', views.setup_wizard, name='setup_wizard'),
    path('setup/skip/', views.skip_setup, name='skip_setup'),

    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),

    # Products
    path('shop/', views.ProductListView.as_view(), name='product_list'),
    path('shop/category/<slug:category_slug>/', views.ProductListView.as_view(), name='category'),
    path('shop/product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('shop/search/', views.ProductSearchView.as_view(), name='search'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Reviews
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),

    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),

    # Payment
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),

    # Orders
    path('orders/', views.order_history, name='order_history'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
]
