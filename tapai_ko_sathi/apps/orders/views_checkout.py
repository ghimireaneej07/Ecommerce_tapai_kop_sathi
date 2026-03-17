"""
Production-Ready Checkout View
- Transaction-safe order creation
- Session cart-to-user cart migration
- Stock management with locking
- Payment initialization
"""
import uuid
import logging
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tapai_ko_sathi.core.utils import api_response, api_error
from tapai_ko_sathi.apps.accounts.models import Address
from tapai_ko_sathi.apps.cart.models import Cart, CartItem
from tapai_ko_sathi.apps.orders.models import Order, OrderItem
from tapai_ko_sathi.apps.payments.models import Payment, PaymentLog
from tapai_ko_sathi.apps.products.models import Product

logger = logging.getLogger(__name__)


def _get_or_create_user_cart(user):
    """Get or create cart for authenticated user"""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def _get_session_cart(session_key):
    """Get cart by session key"""
    return Cart.objects.filter(session_key=session_key).first()


def _merge_session_cart_on_login(request):
    """Merge guest cart into user cart when user logs in"""
    session_cart = _get_session_cart(request.session.session_key)
    if session_cart and request.user.is_authenticated:
        user_cart = _get_or_create_user_cart(request.user)
        user_cart.merge_from_session(session_cart)
        logger.info(f"Merged session cart into user {request.user.email}")


def _generate_order_number():
    """Generate unique order number"""
    return f"TKS-{uuid.uuid4().hex[:12].upper()}"


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic(durable=True)
def create_checkout(request):
    """
    Create order from cart with transaction safety.
    
    Request payload:
    {
        "address_id": 123 (or null to use default),
        "payment_method": "razorpay",
        "use_default_address": true
    }
    """
    user = request.user
    cart = _get_or_create_user_cart(user)
    
    if not cart.items.exists():
        return api_error(
            message="Your cart is empty",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate payment method
    payment_method = request.data.get('payment_method', 'razorpay')
    if payment_method not in ['razorpay', 'esewa', 'cod']:
        return api_error("Invalid payment method")
    
    # Get shipping address
    address_id = request.data.get('address_id')
    use_default = request.data.get('use_default_address', True)
    
    if use_default:
        address = user.profile.default_address if hasattr(user, 'profile') else None
    else:
        address = Address.objects.filter(id=address_id, user=user).first()
    
    if not address:
        return api_error(
            message="Please select a shipping address",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic(durable=True):
            # Lock products for update
            cart_items = list(cart.items.select_related('product'))
            product_ids = [item.product_id for item in cart_items]
            products = Product.objects.select_for_update().filter(id__in=product_ids)
            product_map = {p.id: p for p in products}
            
            # Validate stock
            for item in cart_items:
                product = product_map.get(item.product_id)
                if not product or not product.is_active:
                    raise ValueError(f"Product {item.product.name} is unavailable")
                if product.stock < item.quantity:
                    raise ValueError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {product.stock}, Requested: {item.quantity}"
                    )
            
            # Calculate totals
            subtotal = sum(
                item.product.price * item.quantity 
                for item in cart_items
            )
            shipping_cost = Decimal('50.00')  # Fixed shipping for now
            tax = subtotal * Decimal('0.13')  # 13% VAT for Nepal
            total = subtotal + shipping_cost + tax
            
            # Create order
            order = Order.objects.create(
                user=user,
                order_number=_generate_order_number(),
                status='pending',
                payment_method=payment_method,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax=tax,
                total_amount=total,
                shipping_full_name=address.full_name,
                shipping_phone=address.phone_number,
                shipping_street_address=address.street_address,
                shipping_apartment_address=address.apartment_address,
                shipping_city=address.city,
                shipping_state=address.state,
                shipping_country=address.country,
                shipping_postal_code=address.postal_code,
            )
            
            # Create order items and deduct stock
            for item in cart_items:
                product = product_map[item.product_id]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    unit_price=product.price,
                )
                # Deduct stock safely
                Product.objects.filter(id=product.id).update(
                    stock=Decimal(product.stock) - item.quantity
                )
            
            logger.info(
                f"Order {order.order_number} created for user {user.email} "
                f"with amount NPR {total}"
            )
            
            # Clear cart
            cart.clear()
            
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                gateway=payment_method,
                amount=total,
                currency='NPR',
                status='initiated'
            )
            
            PaymentLog.objects.create(
                payment=payment,
                status='initiated',
                message=f'Payment initiated for order {order.order_number}'
            )
            
            return api_response(
                data={
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'amount': str(total),
                    'payment_method': payment_method,
                },
                message='Order created successfully',
                status_code=status.HTTP_201_CREATED
            )
    
    except ValueError as e:
        logger.warning(f"Checkout error for user {user.email}: {str(e)}")
        return api_error(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Unexpected error in checkout: {str(e)}", exc_info=True)
        return api_error(
            message="Error creating order. Please try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_razorpay_payment(request):
    """
    Verify Razorpay payment signature and update order status.
    
    Request payload:
    {
        "razorpay_order_id": "order_xxx",
        "razorpay_payment_id": "pay_xxx",
        "razorpay_signature": "signature_xxx"
    }
    """
    import hmac
    import hashlib
    
    razorpay_order_id = request.data.get('razorpay_order_id')
    razorpay_payment_id = request.data.get('razorpay_payment_id')
    razorpay_signature = request.data.get('razorpay_signature')
    
    from django.conf import settings
    
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return api_error("Missing payment details")
    
    # Verify signature
    message = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if razorpay_signature != expected_signature:
        logger.warning(f"Invalid Razorpay signature for order {razorpay_order_id}")
        return api_error(
            message="Payment verification failed",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get payment record by transaction_id
        payment = Payment.objects.select_related('order').filter(
            transaction_id=razorpay_order_id
        ).first()
        
        if not payment:
            return api_error("Payment record not found")
        
        # Verify payment belongs to request user
        if payment.order.user != request.user:
            return api_error(
                message="Unauthorized",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        with transaction.atomic(durable=True):
            payment.transaction_id = razorpay_payment_id
            payment.payment_signature = razorpay_signature
            payment.mark_as_verified()
            payment.mark_as_paid()
            
            # Update order status
            payment.order.status = 'confirmed'
            payment.order.save(update_fields=['status'])
            
            PaymentLog.objects.create(
                payment=payment,
                status='success',
                message=f'Payment verified for order {payment.order.order_number}'
            )
            
            logger.info(
                f"Payment verified for order {payment.order.order_number} "
                f"from user {request.user.email}"
            )
        
        return api_response(
            data={
                'order_number': payment.order.order_number,
                'status': payment.order.status,
            },
            message='Payment verified successfully'
        )
    
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}", exc_info=True)
        return api_error(
            message="Error processing payment verification",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
