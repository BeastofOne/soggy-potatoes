from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Cart


@receiver(user_logged_in)
def merge_session_cart(sender, request, user, **kwargs):
    """Move a guest's cart items into their account cart when they log in.

    Login rotates the session key, so the guest cart is found via the
    cart_id stashed in the session by get_or_create_cart (session data
    survives key rotation).
    """
    cart_id = request.session.pop('cart_id', None)
    if not cart_id:
        return

    try:
        session_cart = Cart.objects.get(id=cart_id, user__isnull=True)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)
    for item in session_cart.items.all():
        existing = user_cart.items.filter(product=item.product).first()
        if existing:
            existing.quantity = min(
                existing.quantity + item.quantity,
                item.product.max_order_quantity,
            )
            existing.save()
        else:
            item.cart = user_cart
            item.save()
    session_cart.delete()
