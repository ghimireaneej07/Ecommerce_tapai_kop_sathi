"""
Production-Ready Payment API URLs
- Payment initialization
- Status checking
- Gateway callbacks
- Webhook validation
"""
from django.urls import path
from . import api_views
from . import webhook

app_name = 'payments_api'

urlpatterns = [
    # Payment initialization
    path('orders/<int:order_id>/initiate/', api_views.initiate_razorpay_payment, name='initiate'),
    
    # Payment status
    path('orders/<int:order_id>/status/', api_views.get_payment_status, name='status'),
    
    # Payment verification (after client-side capture)
    path('verify/', api_views.verify_payment, name='verify'),
    
    # Webhooks
    path('webhook/razorpay/', webhook.razorpay_webhook, name='razorpay_webhook'),
]
