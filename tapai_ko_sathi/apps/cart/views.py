from rest_framework import permissions, status, views
from rest_framework.response import Response
from django.shortcuts import render

from .models import Cart, CartItem
from .serializers import CartSerializer
from tapai_ko_sathi.apps.products.models import Product


def _get_or_create_cart(request):
    from .context_processors import _get_or_create_cart as cp_get_cart

    return cp_get_cart(request)


class CartDetailAPI(views.APIView):
    """
    Returns the current user's/session's cart.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = _get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartAddItemAPI(views.APIView):
    """
    Add or increment an item in the cart.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, product_id):
        cart = _get_or_create_cart(request)
        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": 1}
        )
        if not created:
            item.quantity += 1
            item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartRemoveItemAPI(views.APIView):
    """
    Remove an item from the cart completely.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, item_id):
        cart = _get_or_create_cart(request)
        CartItem.objects.filter(cart=cart, id=item_id).delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


def cart_page(request):
    cart = _get_or_create_cart(request)
    return render(request, "cart/cart.html", {"cart": cart})

