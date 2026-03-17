"""
Production-Ready Payment API Views
- Razorpay order initialization
- Payment status tracking
- Payment verification endpoint
"""
import logging
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from tapai_ko_sathi.core.utils import api_response, api_error
from .models import Payment, Order
from .razorpay_utils import RazorpayClient, RazorpayIntegrationError, process_razorpay_payment

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_razorpay_payment(request, order_id):
    """
    Initialize Razorpay payment for an order.
    
    Creates a Razorpay order and returns order details for client-side
    integration with Razorpay Checkout.
    
    Returns:
    {
        "razorpay_order_id": "order_xxx",
        "razorpay_key_id": "rzp_live_xxx",
        "amount": 10000,  // in paise
        "order_number": "TKS-xxx",
        "customer_name": "John Doe",
        "customer_email": "john@example.com"
    }
    """
    user = request.user
    
    # Get order
    order = get_object_or_404(
        Order,
        id=order_id,
        user=user,
        status='pending'
    )
    
    try:
        # Check if payment already exists
        payment = Payment.objects.filter(order=order).first()
        
        if not payment:
            payment = Payment.objects.create(
                order=order,
                gateway='razorpay',
                amount=order.total_amount,
                currency='INR',
                status='initiated'
            )
        
        # Skip if payment already initiated
        if payment.transaction_id:
            return api_response(
                data={
                    'razorpay_order_id': payment.transaction_id,
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'amount': int(payment.amount * 100),
                    'order_number': order.order_number,
                    'customer_name': user.get_full_name() or user.email,
                    'customer_email': user.email,
                }
            )
        
        # Create Razorpay order
        client = RazorpayClient()
        razorpay_order = client.create_order(
            order_id=order.id,
            amount=order.total_amount,
            currency='INR',
            notes={
                'order_number': order.order_number,
                'customer_email': user.email,
            }
        )
        
        # Save Razorpay order ID
        payment.transaction_id = razorpay_order['id']
        payment.save(update_fields=['transaction_id'])
        
        logger.info(
            f"Razorpay order {razorpay_order['id']} created for "
            f"Django order {order.order_number}"
        )
        
        return api_response(
            data={
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': razorpay_order['amount'],
                'order_number': order.order_number,
                'customer_name': user.get_full_name() or user.email,
                'customer_email': user.email,
            },
            message='Payment initialized successfully'
        )
    
    except RazorpayIntegrationError as e:
        logger.error(f"Razorpay error: {str(e)}")
        return api_error(
            message="Failed to initialize payment. Please try again.",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error initializing payment: {str(e)}", exc_info=True)
        return api_error(
            message="Error initializing payment",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status(request, order_id):
    """
    Get current payment status for an order.
    
    Returns payment status, transaction details, and error messages if any.
    """
    user = request.user
    
    # Get order
    order = get_object_or_404(Order, id=order_id, user=user)
    
    # Get payment
    payment = Payment.objects.filter(order=order).first()
    
    if not payment:
        return api_error(
            message="No payment found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return api_response(
        data={
            'order_id': order.id,
            'order_number': order.order_number,
            'order_status': order.status,
            'payment_status': payment.status,
            'payment_id': payment.id,
            'amount': str(payment.amount),
            'transaction_id': payment.transaction_id,
            'is_verified': payment.is_verified,
            'error_message': payment.error_message,
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    Verify Razorpay payment after successful capture.
    
    This endpoint should be called from the client after Razorpay checkout
    successfully captures the payment. The signature verification ensures
    the payment was actually successful.
    
    Request payload:
    {
        "order_id": 123,
        "razorpay_order_id": "order_xxx",
        "razorpay_payment_id": "pay_xxx",
        "razorpay_signature": "signature_xxx"
    }
    """
    user = request.user
    order_id = request.data.get('order_id')
    razorpay_payment_id = request.data.get('razorpay_payment_id')
    razorpay_signature = request.data.get('razorpay_signature')
    
    if not all([order_id, razorpay_payment_id, razorpay_signature]):
        return api_error("Missing required payment details")
    
    # Get order
    try:
        order = Order.objects.select_related('payment').get(
            id=order_id,
            user=user
        )
    except Order.DoesNotExist:
        return api_error(
            message="Order not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Get payment
    payment = order.payment
    if not payment:
        return api_error(
            message="No payment found for order",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    try:
        # Process payment
        result = process_razorpay_payment(
            payment,
            razorpay_payment_id,
            razorpay_signature
        )
        
        return api_response(
            data={
                'order_number': order.order_number,
                'order_status': 'confirmed',
                'payment_status': 'success',
                'message': 'Payment verified successfully'
            },
            message='Payment verified successfully'
        )
    
    except Exception as e:
        logger.error(f"Payment verification failed: {str(e)}")
        return api_error(
            message=str(e) if "signature" in str(e).lower() else "Payment verification failed",
            status_code=status.HTTP_400_BAD_REQUEST
        )
