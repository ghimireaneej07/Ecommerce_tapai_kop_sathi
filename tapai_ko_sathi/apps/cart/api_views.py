"""
Production-Ready Cart System with Session-to-User Merging
- Guest cart management (session-based)
- User cart management (persistent)
- Seamless session-to-user migration on login
- Real-time cart operations with AJAX support
"""
import logging
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.db.models import F, Sum, DecimalField
from django.db.models.functions import Coalesce
from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from tapai_ko_sathi.core.utils import api_response, api_error
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from tapai_ko_sathi.apps.products.models import Product

logger = logging.getLogger(__name__)


def _get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart, 'user'
    else:
        # Create session if doesn't exist
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart, 'session'


def _cart_to_dict(cart):
    """Convert cart to response dictionary"""
    items = cart.items.select_related('product').values(
        'id',
        'product_id',
        'product__name',
        'product__image',
        'product__price',
        'quantity'
    )
    
    items_list = []
    total_items = 0
    total_price = Decimal('0.00')
    
    for item in items:
        item_total = item['product__price'] * item['quantity']
        items_list.append({
            'id': item['id'],
            'product_id': item['product_id'],
            'product_name': item['product__name'],
            'product_image': item['product__image'],
            'price': str(item['product__price']),
            'quantity': item['quantity'],
            'item_total': str(item_total),
        })
        total_items += item['quantity']
        total_price += item_total
    
    return {
        'items': items_list,
        'total_items': total_items,
        'total_price': str(total_price),
        'item_count': len(items_list),
    }


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def cart_view(request):
    """
    Get or update cart.
    
    GET: Retrieve current cart contents
    POST: Update cart (add/remove items)
    """
    cart, cart_type = _get_or_create_cart(request)
    
    if request.method == 'GET':
        return api_response(
            data=_cart_to_dict(cart),
            message='Cart retrieved successfully'
        )
    
    # POST - Add/update item
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    action = request.data.get('action', 'add')  # add, update, remove
    
    if not product_id:
        return api_error("product_id is required")
    
    try:
        quantity = int(quantity)
        if quantity < 0:
            return api_error("Quantity must be positive")
    except (ValueError, TypeError):
        return api_error("Invalid quantity")
    
    # Get product
    product = get_object_or_404(Product, id=product_id)
    
    if not product.is_active:
        return api_error("Product is not available")
    
    try:
        if action == 'add':
            # Add or increment item
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                if item.quantity + quantity > product.stock:
                    return api_error(
                        f"Not enough stock. Available: {product.stock}",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                item.quantity += quantity
                item.save()
            
            logger.info(
                f"Added {quantity} of {product.name} to "
                f"{cart_type} cart"
            )
        
        elif action == 'update':
            # Update quantity
            if quantity == 0:
                CartItem.objects.filter(cart=cart, product=product).delete()
                logger.info(
                    f"Removed {product.name} from {cart_type} cart"
                )
            else:
                if quantity > product.stock:
                    return api_error(
                        f"Not enough stock. Available: {product.stock}",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                CartItem.objects.filter(
                    cart=cart,
                    product=product
                ).update(quantity=quantity)
                logger.info(
                    f"Updated {product.name} quantity to {quantity}"
                )
        
        elif action == 'remove':
            # Remove item
            CartItem.objects.filter(cart=cart, product=product).delete()
            logger.info(f"Removed {product.name} from {cart_type} cart")
        
        else:
            return api_error("Invalid action")
        
        return api_response(
            data=_cart_to_dict(cart),
            message='Cart updated successfully',
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"Error updating cart: {str(e)}", exc_info=True)
        return api_error(
            message="Error updating cart",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def clear_cart(request):
    """Clear all items from cart"""
    cart, cart_type = _get_or_create_cart(request)
    
    try:
        CartItem.objects.filter(cart=cart).delete()
        logger.info(f"Cleared {cart_type} cart")
        
        return api_response(
            data=_cart_to_dict(cart),
            message='Cart cleared successfully'
        )
    
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        return api_error(
            message="Error clearing cart",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def merge_guest_cart_on_login(request):
    """
    Merge guest cart into user cart after login.
    
    Call this endpoint after successful authentication to migrate
    guest cart contents to the authenticated user's persistent cart.
    
    Request body:
    {
        "session_key": "guest_session_key_from_before_login"
    }
    """
    user = request.user
    session_key = request.data.get('session_key')
    
    if not session_key:
        # If no session key provided, just create user cart if needed
        Cart.objects.get_or_create(user=user)
        return api_response(
            message='User cart ready'
        )
    
    try:
        # Get guest cart
        guest_cart = Cart.objects.filter(session_key=session_key).first()
        
        if not guest_cart or not guest_cart.items.exists():
            # No guest cart or empty, just create user cart
            Cart.objects.get_or_create(user=user)
            logger.info(f"No guest cart found for session {session_key}")
            return api_response(
                message='User cart ready'
            )
        
        # Get or create user cart
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        # Merge items
        user_cart.merge_from_session(guest_cart)
        
        logger.info(
            f"Merged guest cart (session {session_key}) into "
            f"user cart for {user.email}"
        )
        
        return api_response(
            data=_cart_to_dict(user_cart),
            message='Guest cart merged successfully'
        )
    
    except Exception as e:
        logger.error(f"Error merging carts: {str(e)}", exc_info=True)
        return api_error(
            message="Error merging cart",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart_count(request):
    """
    Get cart item count for header/navbar.
    
    Returns total number of items in cart.
    """
    cart, cart_type = _get_or_create_cart(request)
    
    total_items = cart.items.aggregate(
        total=Coalesce(Sum('quantity'), 0)
    )['total']
    
    return api_response(
        data={'count': total_items}
    )
