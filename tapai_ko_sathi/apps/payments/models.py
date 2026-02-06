from django.db import models

from tapai_ko_sathi.apps.orders.models import Order


class Payment(models.Model):
    """
    Stores gateway-specific payment data separately from the Order.
    """

    GATEWAY_CHOICES = [
        ("esewa", "eSewa"),
        ("razorpay", "Razorpay / UPI"),
        ("cod", "Cash on Delivery"),
        ("upi", "UPI (Direct)"),
    ]

    order = models.OneToOneField(
        Order, related_name="payment", on_delete=models.CASCADE
    )
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="NPR")
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("initiated", "Initiated"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        default="initiated",
    )
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["gateway", "transaction_id"])]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Payment for {self.order.order_number} via {self.gateway}"

