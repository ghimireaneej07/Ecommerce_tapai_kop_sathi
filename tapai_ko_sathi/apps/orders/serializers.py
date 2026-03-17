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
        fields = ["id", "product", "quantity", "unit_price", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    # Expose shipping fields with simpler aliases for the API
    full_name = serializers.CharField(source="shipping_full_name", required=True)
    phone = serializers.CharField(source="shipping_phone", required=True)
    address_line1 = serializers.CharField(source="shipping_street_address", required=True)
    address_line2 = serializers.CharField(source="shipping_apartment_address", required=False, allow_blank=True)
    city = serializers.CharField(source="shipping_city", required=True)
    postal_code = serializers.CharField(source="shipping_postal_code", required=False, allow_blank=True)

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

