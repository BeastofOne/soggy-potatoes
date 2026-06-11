"""
Tests for the shop app.

Run with: python manage.py test shop
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Wishlist, Review


class CategoryModelTest(TestCase):
    """Tests for the Category model."""

    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            description='A test category'
        )

    def test_category_creation(self):
        """Test that category is created correctly."""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertTrue(self.category.is_active)

    def test_category_str(self):
        """Test category string representation."""
        self.assertEqual(str(self.category), 'Test Category')


class ProductModelTest(TestCase):
    """Tests for the Product model."""

    def setUp(self):
        self.category = Category.objects.create(
            name='Stickers',
            slug='stickers'
        )
        self.product = Product.objects.create(
            name='Cute Cat Sticker',
            slug='cute-cat-sticker',
            description='A very cute cat sticker',
            price=Decimal('3.99'),
            stock=100,
            category=self.category
        )

    def test_product_creation(self):
        """Test that product is created correctly."""
        self.assertEqual(self.product.name, 'Cute Cat Sticker')
        self.assertEqual(self.product.price, Decimal('3.99'))
        self.assertEqual(self.product.stock, 100)
        self.assertTrue(self.product.is_active)

    def test_product_str(self):
        """Test product string representation."""
        self.assertEqual(str(self.product), 'Cute Cat Sticker')

    def test_current_price_no_sale(self):
        """Test current_price returns regular price when no sale."""
        self.assertEqual(self.product.current_price, Decimal('3.99'))

    def test_current_price_with_sale(self):
        """Test current_price returns sale_price when on sale."""
        self.product.sale_price = Decimal('2.99')
        self.product.save()
        self.assertEqual(self.product.current_price, Decimal('2.99'))

    def test_is_on_sale(self):
        """Test is_on_sale property."""
        self.assertFalse(self.product.is_on_sale)
        self.product.sale_price = Decimal('2.99')
        self.product.save()
        self.assertTrue(self.product.is_on_sale)

    def test_in_stock_made_to_order(self):
        """Products that don't track inventory are always in stock."""
        self.product.track_inventory = False
        self.product.stock = 0
        self.product.save()
        self.assertTrue(self.product.in_stock)

    def test_in_stock_tracked(self):
        """Products that track inventory follow the stock count."""
        self.product.track_inventory = True
        self.product.save()
        self.assertTrue(self.product.in_stock)
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.in_stock)

    def test_can_fulfill_made_to_order(self):
        """Made-to-order products accept any quantity up to the per-order cap."""
        self.product.track_inventory = False
        self.product.stock = 0
        self.product.save()
        self.assertTrue(self.product.can_fulfill(1))
        self.assertTrue(self.product.can_fulfill(Product.MAX_ORDER_QUANTITY))
        self.assertFalse(self.product.can_fulfill(Product.MAX_ORDER_QUANTITY + 1))
        self.assertFalse(self.product.can_fulfill(0))

    def test_can_fulfill_tracked(self):
        """Tracked products are limited by stock."""
        self.product.track_inventory = True
        self.product.stock = 3
        self.product.save()
        self.assertTrue(self.product.can_fulfill(3))
        self.assertFalse(self.product.can_fulfill(4))

    def test_reduce_stock_only_when_tracked(self):
        """reduce_stock decrements tracked products and ignores made-to-order ones."""
        self.product.track_inventory = True
        self.product.stock = 5
        self.product.save()
        self.product.reduce_stock(2)
        self.assertEqual(self.product.stock, 3)
        # Never goes negative
        self.product.reduce_stock(10)
        self.assertEqual(self.product.stock, 0)

        self.product.track_inventory = False
        self.product.stock = 5
        self.product.save()
        self.product.reduce_stock(2)
        self.assertEqual(self.product.stock, 5)


class CartModelTest(TestCase):
    """Tests for the Cart and CartItem models."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Stickers', slug='stickers')
        self.product = Product.objects.create(
            name='Test Sticker',
            slug='test-sticker',
            price=Decimal('4.99'),
            stock=50,
            category=self.category
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        """Test that cart is created correctly."""
        self.assertEqual(self.cart.user, self.user)

    def test_add_item_to_cart(self):
        """Test adding items to cart."""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(self.cart.total_items, 2)

    def test_cart_subtotal(self):
        """Test cart subtotal calculation."""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(self.cart.subtotal, Decimal('14.97'))

    def test_cart_item_total_price(self):
        """Test cart item total price."""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart_item.total_price, Decimal('9.98'))


class OrderModelTest(TestCase):
    """Tests for the Order model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Stickers', slug='stickers')
        self.product = Product.objects.create(
            name='Test Sticker',
            slug='test-sticker',
            price=Decimal('4.99'),
            stock=50,
            category=self.category
        )

    def test_order_creation(self):
        """Test that order is created with auto-generated order number."""
        order = Order.objects.create(
            user=self.user,
            email='test@example.com',
            shipping_name='Test User',
            shipping_address='123 Test St',
            shipping_city='Test City',
            shipping_state='TS',
            shipping_zip='12345',
            shipping_country='United States',
            subtotal=Decimal('4.99'),
            total=Decimal('4.99')
        )
        self.assertTrue(order.order_number.startswith('SP-'))
        self.assertEqual(order.status, 'pending')

    def test_order_item_creation(self):
        """Test creating order items."""
        order = Order.objects.create(
            user=self.user,
            email='test@example.com',
            shipping_name='Test User',
            shipping_address='123 Test St',
            shipping_city='Test City',
            shipping_state='TS',
            shipping_zip='12345',
            shipping_country='United States',
            subtotal=Decimal('9.98'),
            total=Decimal('9.98')
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name='Test Sticker',
            product_price=Decimal('4.99'),
            quantity=2
        )
        self.assertEqual(order_item.total_price, Decimal('9.98'))


class ViewsTest(TestCase):
    """Tests for shop views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Stickers', slug='stickers')
        self.product = Product.objects.create(
            name='Test Sticker',
            slug='test-sticker',
            price=Decimal('4.99'),
            stock=50,
            category=self.category,
            is_active=True
        )

    def test_home_view(self):
        """Test home page loads successfully."""
        response = self.client.get(reverse('shop:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/home.html')

    def test_product_list_view(self):
        """Test product list page loads successfully."""
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Sticker')

    def test_product_detail_view(self):
        """Test product detail page loads successfully."""
        response = self.client.get(
            reverse('shop:product_detail', kwargs={'slug': 'test-sticker'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Sticker')
        self.assertContains(response, '4.99')

    def test_cart_view(self):
        """Test cart page loads successfully."""
        response = self.client.get(reverse('shop:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/cart.html')

    def test_add_to_cart(self):
        """Test adding product to cart."""
        response = self.client.post(
            reverse('shop:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to cart

    def test_checkout_requires_login(self):
        """Test that checkout requires authentication."""
        response = self.client.get(reverse('shop:checkout'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_checkout_logged_in(self):
        """Test checkout page for logged-in user."""
        self.client.login(username='testuser', password='testpass123')
        # Add item to cart first
        self.client.post(
            reverse('shop:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )
        response = self.client.get(reverse('shop:checkout'))
        self.assertEqual(response.status_code, 200)

    def test_search_view(self):
        """Test product search."""
        response = self.client.get(reverse('shop:search'), {'q': 'sticker'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Sticker')


class MadeToOrderPurchaseTest(TestCase):
    """A stock=0 made-to-order product must be purchasable end to end."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer', email='buyer@example.com', password='testpass123'
        )
        self.product = Product.objects.create(
            name='Made To Order Sticker',
            slug='made-to-order-sticker',
            description='Printed when you order it',
            price=Decimal('3.99'),
            stock=0,
            track_inventory=False,
            is_active=True,
        )

    def test_add_to_cart_with_zero_stock(self):
        """Adding a made-to-order product to the cart succeeds despite stock=0."""
        response = self.client.post(
            reverse('shop:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(session_key=self.client.session.session_key)
        self.assertEqual(cart.total_items, 2)

    def test_checkout_with_zero_stock(self):
        """Checkout page loads for a cart holding made-to-order items."""
        self.client.login(username='buyer', password='testpass123')
        self.client.post(
            reverse('shop:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )
        response = self.client.get(reverse('shop:checkout'))
        self.assertEqual(response.status_code, 200)

    def test_quantity_dropdown_rendered(self):
        """Product page shows quantity options for made-to-order products."""
        response = self.client.get(
            reverse('shop:product_detail', kwargs={'slug': self.product.slug})
        )
        self.assertContains(response, '<option value="1">')


class CartMergeOnLoginTest(TestCase):
    """Guest carts must survive logging in at checkout."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='shopper', email='shopper@example.com', password='testpass123'
        )
        self.product = Product.objects.create(
            name='Merge Sticker',
            slug='merge-sticker',
            description='test',
            price=Decimal('2.99'),
            track_inventory=False,
            is_active=True,
        )

    def test_guest_cart_merges_into_user_cart(self):
        self.client.post(
            reverse('shop:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        self.client.login(username='shopper', password='testpass123')

        user_cart = Cart.objects.get(user=self.user)
        self.assertEqual(user_cart.total_items, 2)
        # Guest cart is gone
        self.assertFalse(Cart.objects.filter(user__isnull=True).exists())


class WishlistTest(TestCase):
    """Tests for wishlist functionality."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Stickers', slug='stickers')
        self.product = Product.objects.create(
            name='Test Sticker',
            slug='test-sticker',
            price=Decimal('4.99'),
            stock=50,
            category=self.category,
            is_active=True
        )

    def test_wishlist_requires_login(self):
        """Test that wishlist requires authentication."""
        response = self.client.get(reverse('shop:wishlist'))
        self.assertEqual(response.status_code, 302)

    def test_toggle_wishlist(self):
        """Test adding and removing from wishlist."""
        self.client.login(username='testuser', password='testpass123')

        # Add to wishlist
        response = self.client.post(
            reverse('shop:toggle_wishlist', kwargs={'product_id': self.product.id})
        )
        self.assertEqual(response.status_code, 302)

        wishlist = Wishlist.objects.get(user=self.user)
        self.assertTrue(wishlist.products.filter(pk=self.product.pk).exists())

        # Remove from wishlist
        response = self.client.post(
            reverse('shop:toggle_wishlist', kwargs={'product_id': self.product.id})
        )
        self.assertFalse(wishlist.products.filter(pk=self.product.pk).exists())


class ReviewTest(TestCase):
    """Tests for review functionality."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Stickers', slug='stickers')
        self.product = Product.objects.create(
            name='Test Sticker',
            slug='test-sticker',
            price=Decimal('4.99'),
            stock=50,
            category=self.category,
            is_active=True
        )

    def test_add_review(self):
        """Test adding a review."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('shop:add_review', kwargs={'product_id': self.product.id}),
            {
                'rating': 5,
                'title': 'Great sticker!',
                'comment': 'Love this sticker, very cute!'
            }
        )
        self.assertEqual(response.status_code, 302)

        review = Review.objects.get(user=self.user, product=self.product)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, 'Great sticker!')

    def test_cannot_review_twice(self):
        """Test that user cannot review same product twice."""
        self.client.login(username='testuser', password='testpass123')

        # First review
        self.client.post(
            reverse('shop:add_review', kwargs={'product_id': self.product.id}),
            {'rating': 5, 'title': 'Great!', 'comment': 'Love it!'}
        )

        # Second review should fail
        self.client.post(
            reverse('shop:add_review', kwargs={'product_id': self.product.id}),
            {'rating': 4, 'title': 'Good', 'comment': 'Still good'}
        )

        # Should still only have one review
        self.assertEqual(
            Review.objects.filter(user=self.user, product=self.product).count(),
            1
        )
