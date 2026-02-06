from django.conf import settings
from django.db import models

from tapai_ko_sathi.apps.products.models import Product


class Order(models.Model):
    """
    Represents a confirmed checkout with address and payment info.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("shipped", "Shipped"),
        ("completed", "Completed"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("esewa", "eSewa"),
        ("razorpay", "Razorpay"),
        ("cod", "Cash on Delivery"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        on_delete=models.CASCADE,
    )
    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["order_number", "status"])]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity

