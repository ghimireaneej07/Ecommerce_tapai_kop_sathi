"""
Razorpay Payment Webhook Handler
- Process payment completion webhooks
- Security validation
- Idempotent webhook handling
"""
import json
import logging
from decimal import Decimal

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from tapai_ko_sathi.core.utils import api_response, api_error
from .models import Payment, PaymentLog
from .razorpay_utils import (
    validate_razorpay_webhook,
    process_razorpay_payment,
    RazorpayIntegrationError
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(['POST'])
def razorpay_webhook(request):
    """
    Razorpay webhook endpoint for payment status updates.
    
    Webhook signature is verified using RAZORPAY_KEY_SECRET.
    Webhook events:
    - payment.authorized
    - payment.failed
    - payment.captured
    - refund.created
    
    Security:
    - All requests must have valid X-Razorpay-Signature header
    - Webhook is idempotent - can be called multiple times safely
    """
    
    # Get webhook signature from header
    razorpay_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')
    
    if not razorpay_signature:
        logger.warning("Webhook request without signature header")
        return JsonResponse({'error': 'Missing signature'}, status=400)
    
    try:
        # Validate webhook signature
        if not validate_razorpay_webhook(request.body, razorpay_signature):
            logger.warning("Invalid webhook signature")
            return JsonResponse({'error': 'Invalid signature'}, status=403)
        
        # Parse webhook payload
        webhook_data = json.loads(request.body.decode('utf-8'))
        event = webhook_data.get('event')
        payload = webhook_data.get('payload', {})
        
        logger.info(f"Webhook received: {event}")
        
        # Dispatch to appropriate handler
        if event == 'payment.authorized':
            return handle_payment_authorized(payload)
        elif event == 'payment.captured':
            return handle_payment_captured(payload)
        elif event == 'payment.failed':
            return handle_payment_failed(payload)
        elif event == 'refund.created':
            return handle_refund_created(payload)
        else:
            logger.warning(f"Unhandled webhook event: {event}")
            return JsonResponse({'status': 'ok'})  # Acknowledge but don't process
    
    except json.JSONDecodeError:
        logger.error("Failed to parse webhook JSON")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)


def handle_payment_authorized(payload):
    """Handle payment.authorized webhook"""
    payment_data = payload.get('payment', {})
    order_id = payment_data.get('order_id')
    payment_id = payment_data.get('id')
    
    try:
        payment = Payment.objects.select_related('order').get(
            transaction_id=order_id
        )
        
        # Idempotent check - if already captured, skip
        if payment.status in ['success', 'captured']:
            logger.info(f"Payment {payment_id} already processed")
            return JsonResponse({'status': 'ok'})
        
        with transaction.atomic(durable=True):
            payment.transaction_id = payment_id
            payment.status = 'authorized'
            payment.save(update_fields=['transaction_id', 'status'])
            
            PaymentLog.objects.create(
                payment=payment,
                status='authorized',
                message=f'Payment {payment_id} authorized',
                metadata={
                    'razorpay_payment_id': payment_id,
                    'amount': payment_data.get('amount'),
                }
            )
            
            logger.info(f"Payment {payment_id} authorized for order {order_id}")
        
        return JsonResponse({'status': 'ok'})
    
    except Payment.DoesNotExist:
        logger.warning(f"Payment not found for order {order_id}")
        return JsonResponse({'status': 'ok'})  # Acknowledge, may be duplicate


def handle_payment_captured(payload):
    """Handle payment.captured webhook"""
    payment_data = payload.get('payment', {})
    payment_id = payment_data.get('id')
    
    try:
        payment = Payment.objects.select_related('order').get(
            transaction_id=payment_id
        )
        
        # Idempotent check
        if payment.status == 'success':
            return JsonResponse({'status': 'ok'})
        
        with transaction.atomic(durable=True):
            payment.mark_as_paid()
            payment.order.status = 'confirmed'
            payment.order.save(update_fields=['status'])
            
            PaymentLog.objects.create(
                payment=payment,
                status='captured',
                message=f'Payment {payment_id} captured successfully',
                metadata={
                    'razorpay_payment_id': payment_id,
                    'amount': payment_data.get('amount'),
                }
            )
            
            logger.info(f"Payment {payment_id} captured and marked as success")
        
        return JsonResponse({'status': 'ok'})
    
    except Payment.DoesNotExist:
        logger.warning(f"Payment not found: {payment_id}")
        return JsonResponse({'status': 'ok'})


def handle_payment_failed(payload):
    """Handle payment.failed webhook"""
    payment_data = payload.get('payment', {})
    payment_id = payment_data.get('id')
    error_msg = payment_data.get('error_description', 'Unknown error')
    
    try:
        payment = Payment.objects.select_related('order').get(
            transaction_id=payment_id
        )
        
        # Idempotent check
        if payment.status == 'failed':
            return JsonResponse({'status': 'ok'})
        
        with transaction.atomic(durable=True):
            payment.mark_as_failed(error_msg)
            payment.order.status = 'failed'
            payment.order.save(update_fields=['status'])
            
            PaymentLog.objects.create(
                payment=payment,
                status='failed',
                message=f'Payment failed: {error_msg}',
                metadata={
                    'razorpay_payment_id': payment_id,
                    'error': error_msg,
                }
            )
            
            logger.warning(f"Payment {payment_id} failed: {error_msg}")
        
        return JsonResponse({'status': 'ok'})
    
    except Payment.DoesNotExist:
        logger.warning(f"Payment not found for failed event: {payment_id}")
        return JsonResponse({'status': 'ok'})


def handle_refund_created(payload):
    """Handle refund.created webhook"""
    refund_data = payload.get('refund', {})
    payment_id = refund_data.get('payment_id')
    refund_id = refund_data.get('id')
    refund_amount = Decimal(refund_data.get('amount', 0)) / 100
    
    try:
        payment = Payment.objects.select_related('order').get(
            transaction_id=payment_id
        )
        
        with transaction.atomic(durable=True):
            payment.status = 'refunded'
            payment.save(update_fields=['status'])
            
            # Update order if fully refunded
            if refund_amount >= payment.amount:
                payment.order.status = 'cancelled'
                payment.order.save(update_fields=['status'])
            
            PaymentLog.objects.create(
                payment=payment,
                status='refunded',
                message=f'Refund {refund_id} created for amount {refund_amount}',
                metadata={
                    'refund_id': refund_id,
                    'refund_amount': str(refund_amount),
                }
            )
            
            logger.info(f"Refund {refund_id} created for payment {payment_id}")
        
        return JsonResponse({'status': 'ok'})
    
    except Payment.DoesNotExist:
        logger.warning(f"Payment not found for refund: {payment_id}")
        return JsonResponse({'status': 'ok'})
