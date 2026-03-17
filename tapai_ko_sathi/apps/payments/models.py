from django.db import models
from django.utils import timezone
from tapai_ko_sathi.apps.orders.models import Order


class Payment(models.Model):
    """
    Production-ready payment model with complete transaction tracking.
    Stores gateway-specific payment data separately from Order.
    """

    GATEWAY_CHOICES = [
        ("razorpay", "Razorpay / UPI"),
        ("esewa", "eSewa"),
        ("cod", "Cash on Delivery"),
    ]

    STATUS_CHOICES = [
        ("initiated", "Initiated"),
        ("pending", "Pending"),
        ("authorized", "Authorized"),
        ("captured", "Captured"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    order = models.OneToOneField(
        Order, related_name="payment", on_delete=models.CASCADE
    )
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="NPR")
    
    # Transaction tracking
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_signature = models.CharField(max_length=255, blank=True)
    
    # Status and verification
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="initiated",
        db_index=True
    )
    is_verified = models.BooleanField(default=False)
    
    # Raw response data
    raw_response = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["gateway", "transaction_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["order"]),
            models.Index(fields=["paid_at"]),
        ]
        ordering = ["-initiated_at"]

    def __str__(self) -> str:
        return f"Payment {self.transaction_id or self.id} for Order {self.order.order_number}"

    def mark_as_verified(self):
        """Mark payment as verified after signature validation"""
        self.is_verified = True
        self.status = "captured"
        self.verified_at = timezone.now()
        self.save(update_fields=["is_verified", "status", "verified_at"])

    def mark_as_paid(self):
        """Mark payment as completed"""
        self.status = "success"
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])

    def mark_as_failed(self, error_message=""):
        """Mark payment as failed"""
        self.status = "failed"
        self.error_message = error_message
        self.save(update_fields=["status", "error_message"])


class PaymentLog(models.Model):
    """
    Audit log for all payment attempts and status changes.
    """

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=20)
    message = models.TextField()
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Payment Log for {self.payment.order.order_number} - {self.status}"

