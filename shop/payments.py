"""
Stripe payment integration for Soggy Potatoes.

Uses Stripe Checkout Sessions for secure, hosted payment pages.
This keeps credit card handling off our servers (PCI compliant).
"""
import stripe
from django.conf import settings
from django.urls import reverse
from decimal import Decimal

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request, order, success_url, cancel_url):
    """
    Create a Stripe Checkout Session for an order.

    Args:
        request: Django request object
        order: Order model instance
        success_url: URL to redirect on successful payment
        cancel_url: URL to redirect on cancelled payment

    Returns:
        stripe.checkout.Session object
    """
    # Build line items from order
    line_items = []
    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item.product_price * 100),  # Stripe uses cents
                'product_data': {
                    'name': item.product_name,
                    'description': f'Qty: {item.quantity}',
                },
            },
            'quantity': item.quantity,
        })

    # Add shipping as a line item if not free
    if order.shipping_cost > 0:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(order.shipping_cost * 100),
                'product_data': {
                    'name': 'Shipping',
                },
            },
            'quantity': 1,
        })

    # Create Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=order.email,
        metadata={
            'order_id': order.id,
            'order_number': order.order_number,
        },
        shipping_address_collection={
            'allowed_countries': ['US', 'CA'],
        } if not order.shipping_address else None,
    )

    return session


def create_payment_intent(order):
    """
    Create a Stripe PaymentIntent for an order (alternative to Checkout Sessions).

    Use this if you want to build a custom payment form.

    Args:
        order: Order model instance

    Returns:
        stripe.PaymentIntent object
    """
    intent = stripe.PaymentIntent.create(
        amount=int(order.total * 100),  # Amount in cents
        currency='usd',
        metadata={
            'order_id': order.id,
            'order_number': order.order_number,
        },
        receipt_email=order.email,
    )

    return intent


def retrieve_payment_intent(payment_intent_id):
    """
    Retrieve a PaymentIntent by ID.

    Args:
        payment_intent_id: Stripe PaymentIntent ID

    Returns:
        stripe.PaymentIntent object
    """
    return stripe.PaymentIntent.retrieve(payment_intent_id)


def retrieve_checkout_session(session_id):
    """
    Retrieve a Checkout Session by ID.

    Args:
        session_id: Stripe Checkout Session ID

    Returns:
        stripe.checkout.Session object
    """
    return stripe.checkout.Session.retrieve(session_id)


def construct_webhook_event(payload, sig_header):
    """
    Construct and verify a Stripe webhook event.

    Args:
        payload: Raw request body
        sig_header: Stripe-Signature header value

    Returns:
        stripe.Event object

    Raises:
        ValueError: If payload is invalid
        stripe.error.SignatureVerificationError: If signature is invalid
    """
    return stripe.Webhook.construct_event(
        payload,
        sig_header,
        settings.STRIPE_WEBHOOK_SECRET
    )
