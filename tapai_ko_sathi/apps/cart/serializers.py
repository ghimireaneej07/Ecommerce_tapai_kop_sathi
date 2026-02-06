from rest_framework import serializers

from .models import Cart, CartItem
from tapai_ko_sathi.apps.products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "subtotal"]
        read_only_fields = ["subtotal"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "total_items", "total_price", "items"]
        read_only_fields = ["total_items", "total_price", "items"]

