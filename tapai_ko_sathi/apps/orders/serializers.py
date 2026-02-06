from rest_framework import serializers

from .models import Order, OrderItem
from tapai_ko_sathi.apps.products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "payment_method",
            "total_amount",
            "full_name",
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "postal_code",
            "created_at",
            "items",
        ]
        read_only_fields = ["order_number", "status", "total_amount", "created_at"]

