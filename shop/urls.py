from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
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
]
