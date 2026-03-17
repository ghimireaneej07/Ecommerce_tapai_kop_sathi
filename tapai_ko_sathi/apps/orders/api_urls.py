"""
Production-Ready URL Configuration for Orders and Payments
- Checkout endpoints
- Payment gateway integration
- Webhook handlers
"""
from django.urls import path
from . import views_checkout
from tapai_ko_sathi.apps.payments import webhook

app_name = 'orders'

urlpatterns = [
    # Checkout endpoints
    path('checkout/', views_checkout.create_checkout, name='checkout'),
    path('verify-payment/', views_checkout.verify_razorpay_payment, name='verify_payment'),
    
    # Payment webhooks
    path('webhook/razorpay/', webhook.razorpay_webhook, name='razorpay_webhook'),
]
