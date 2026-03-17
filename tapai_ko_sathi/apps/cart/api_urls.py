"""
Production-Ready URL Configuration for Cart API
- Cart operations (add, update, remove, clear)
- Session-to-user cart merging
- Real-time cart count
"""
from django.urls import path
from . import api_views

app_name = 'cart'

urlpatterns = [
    # Cart operations
    path('', api_views.cart_view, name='cart'),
    path('clear/', api_views.clear_cart, name='clear_cart'),
    path('count/', api_views.get_cart_count, name='cart_count'),
    
    # Session merge on login
    path('merge/', api_views.merge_guest_cart_on_login, name='merge_cart'),
]
