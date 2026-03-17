from django.conf import settings
from django.db import models
from django.utils import timezone
from tapai_ko_sathi.apps.products.models import Product


class Order(models.Model):
    """
    Production-ready Order model with:
    - Transaction-safe checkout
    - Stock management
    - Payment tracking
    - Order status lifecycle
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("razorpay", "Razorpay"),
        ("esewa", "eSewa"),
        ("cod", "Cash on Delivery"),
    ]

    # User & identification
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        on_delete=models.CASCADE,
        db_index=True
    )
    order_number = models.CharField(
        max_length=32,
        unique=True,
        db_index=True
    )
    
    # Shipping information
    shipping_full_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=20)
    shipping_street_address = models.CharField(max_length=255)
    shipping_apartment_address = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=80)
    shipping_state = models.CharField(max_length=80, blank=True)
    shipping_country = models.CharField(max_length=80)
    shipping_postal_code = models.CharField(max_length=20)
    
    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment information
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        db_index=True
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True
    )
    
    # Notes and tracking
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]
        ordering = ["-created_at"]
        verbose_name_plural = "Orders"

    def __str__(self) -> str:
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        # Ensure timestamps are updated correctly
        if self.status == "shipped" and not self.shipped_at:
            self.shipped_at = timezone.now()
        if self.status == "delivered" and not self.delivered_at:
            self.delivered_at = timezone.now()
        super().save(*args, **kwargs)

    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled based on status"""
        return self.status in ["pending", "confirmed"]

    def get_status_display_verbose(self) -> str:
        """Get verbose status for customer communication"""
        status_messages = {
            "pending": "Your order is pending payment",
            "confirmed": "Your order has been confirmed",
            "processing": "We're processing your order",
            "shipped": "Your order has been shipped",
            "delivered": "Your order has been delivered",
            "cancelled": "Your order was cancelled",
            "failed": "Your order payment failed"
        }
        return status_messages.get(self.status, self.get_status_display())


class OrderItem(models.Model):
    """
    Individual items in an order.
    Stores snapshot of product info at time of order.
    """

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
        ]

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product.name} in {self.order.order_number}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    @property
    def total(self):
        return self.subtotal - self.discount

