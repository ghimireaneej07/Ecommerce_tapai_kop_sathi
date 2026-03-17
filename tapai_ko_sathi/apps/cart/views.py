from decimal import Decimal
from rest_framework import permissions, status, views
from rest_framework.response import Response
from django.shortcuts import render

from .models import Cart, CartItem
from .serializers import CartSerializer
from tapai_ko_sathi.apps.products.models import Product


def _get_or_create_cart(request):
    from .context_processors import _get_or_create_cart as cp_get_cart

    return cp_get_cart(request)


from tapai_ko_sathi.core.utils import api_response, api_error


def _cart_payload(cart, item=None):
    serializer = CartSerializer(cart)
    payload = {
        "cart": serializer.data,
        "cart_item_count": cart.total_items,
        "cart_total": str(cart.total_price),
    }
    if item:
        payload["item_id"] = item.id
        payload["item_subtotal"] = str(item.subtotal)
    return payload


class CartDetailAPI(views.APIView):
    """
    Returns the current user's/session's cart.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = _get_or_create_cart(request)
        return api_response(data=_cart_payload(cart))


class CartAddItemAPI(views.APIView):
    """
    Add or increment an item in the cart.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, product_id):
        cart = _get_or_create_cart(request)
        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return api_error(message="Product not found", status_code=status.HTTP_404_NOT_FOUND)

        try:
            quantity = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return api_error(message="Invalid quantity")

        if quantity <= 0:
            return api_error(message="Quantity must be at least 1")

        if product.stock < quantity:
            return api_error(message="Not enough stock available")

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )
        if not created:
            if item.quantity + quantity > product.stock:
                return api_error(message="Not enough stock available")
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        return api_response(data=_cart_payload(cart, item=item), message="Item added to cart")


class CartUpdateItemAPI(views.APIView):
    """
    Update the quantity of an item in the cart.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, item_id):
        cart = _get_or_create_cart(request)
        quantity = request.data.get("quantity")
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                CartItem.objects.filter(cart=cart, id=item_id).delete()
            else:
                item = CartItem.objects.filter(cart=cart, id=item_id).select_related("product").first()
                if item:
                    if item.product.stock < quantity:
                        return api_error(message="Not enough stock available")
                    item.quantity = quantity
                    item.save(update_fields=["quantity"])
                else:
                    return api_error(message="Item not found in cart", status_code=status.HTTP_404_NOT_FOUND)
        except (TypeError, ValueError):
            return api_error(message="Invalid quantity")

        payload_item = CartItem.objects.filter(cart=cart, id=item_id).first()
        return api_response(data=_cart_payload(cart, item=payload_item), message="Cart updated")


class CartRemoveItemAPI(views.APIView):
    """
    Remove an item from the cart completely.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, item_id):
        cart = _get_or_create_cart(request)
        CartItem.objects.filter(cart=cart, id=item_id).delete()
        return api_response(data=_cart_payload(cart), message="Item removed from cart")


def cart_page(request):
    cart = _get_or_create_cart(request)
    return render(request, "cart/cart.html", {"cart": cart})

