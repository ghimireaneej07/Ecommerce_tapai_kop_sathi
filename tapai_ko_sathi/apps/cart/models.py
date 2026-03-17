from django.conf import settings
from django.db import models
from decimal import Decimal
from django.db.models import Sum, F
from tapai_ko_sathi.apps.products.models import Product


class Cart(models.Model):
    """
    Production-ready cart system:
    - Guest carts stored via session_key
    - User carts tied to user account
    - Supports session-to-user migration on login
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="cart",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=40, db_index=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["session_key"]),
            models.Index(fields=["updated_at"]),
        ]
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Cart #{self.pk} (Session: {self.session_key[:10]})"

    @property
    def total_items(self) -> int:
        result = self.items.aggregate(total=Sum("quantity"))
        return int(result.get("total") or 0)

    @property
    def total_price(self) -> Decimal:
        result = self.items.aggregate(total=Sum(F("quantity") * F("product__price")))
        return result.get("total") or Decimal("0.00")

    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()

    def merge_from_session(self, session_cart):
        """Merge items from a session cart into this user cart"""
        for session_item in session_cart.items.all():
            existing_item = self.items.filter(product=session_item.product).first()
            if existing_item:
                existing_item.quantity += session_item.quantity
                existing_item.save(update_fields=["quantity"])
            else:
                CartItem.objects.create(
                    cart=self,
                    product=session_item.product,
                    quantity=session_item.quantity
                )
        session_cart.delete()


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity

