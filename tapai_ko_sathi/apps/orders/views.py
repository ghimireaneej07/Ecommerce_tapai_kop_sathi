import uuid
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.db.models import F

from rest_framework import generics, permissions, status
from tapai_ko_sathi.core.utils import api_response, api_error
from .models import Order, OrderItem
from .serializers import OrderSerializer
from tapai_ko_sathi.apps.payments.models import Payment
from tapai_ko_sathi.apps.orders.forms import CheckoutForm
from tapai_ko_sathi.apps.products.models import Product


class OrderListAPI(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(data=serializer.data)


class OrderCreateAPI(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = _get_user_cart(request)
        if not cart or cart.total_items == 0:
            return api_error(message="Your cart is empty", status_code=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = _create_order_from_cart(
                user=request.user,
                cart=cart,
                order_data=serializer.validated_data,
            )
        except ValueError as exc:
            return api_error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)

        return api_response(
            data=OrderSerializer(order).data,
            message="Order created successfully",
            status_code=status.HTTP_201_CREATED
        )


def _get_user_cart(request):
    """
    Reuse the cart helper to fetch the current user's cart.
    """
    from tapai_ko_sathi.apps.cart.context_processors import (
        _get_or_create_cart as cp_get_cart,
    )

    return cp_get_cart(request)


def _generate_order_number() -> str:
    """
    Generate a short, unique order identifier.
    """
    import uuid
    uid = uuid.uuid4().hex
    return f"TKS-{uid[:10].upper()}"


def _create_order_from_cart(user, cart, order_data):
    cart_items = list(cart.items.select_related("product"))
    if not cart_items:
        raise ValueError("Your cart is empty")

    product_ids = [item.product_id for item in cart_items]
    with transaction.atomic():
        products = Product.objects.select_for_update().filter(id__in=product_ids)
        product_map = {product.id: product for product in products}

        total_amount = Decimal("0.00")
        for item in cart_items:
            product = product_map.get(item.product_id)
            if not product or not product.is_active:
                raise ValueError("One or more products are unavailable")
            if product.stock < item.quantity:
                raise ValueError(f"Not enough stock for {product.name}")

            total_amount += product.price * item.quantity

        order = Order.objects.create(
            user=user,
            order_number=_generate_order_number(),
            status="pending",
            subtotal=total_amount,
            total_amount=total_amount,
            payment_method=order_data["payment_method"],
            shipping_full_name=order_data["full_name"],
            shipping_phone=order_data["phone"],
            shipping_street_address=order_data["address_line1"],
            shipping_apartment_address=order_data.get("address_line2", ""),
            shipping_city=order_data["city"],
            shipping_postal_code=order_data.get("postal_code", ""),
            shipping_country="Nepal",
        )

        order_items = []
        for item in cart_items:
            product = product_map[item.product_id]
            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    unit_price=product.price,
                )
            )
            product.stock = F("stock") - item.quantity
            product.save(update_fields=["stock"])

        OrderItem.objects.bulk_create(order_items)

        Payment.objects.create(
            order=order,
            gateway=order.payment_method,
            amount=order.total_amount,
            status="initiated",
        )

        cart.items.all().delete()

    return order


@login_required
def checkout_start(request):
    cart = _get_user_cart(request)
    if not cart or cart.total_items == 0:
        messages.info(request, "Your cart is empty.")
        return redirect("cart_page")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = _create_order_from_cart(
                    user=request.user,
                    cart=cart,
                    order_data=form.cleaned_data,
                )
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect("cart_page")

            payment = order.payment

            if payment.gateway == "cod":
                order.status = "pending"
                order.save()
                messages.success(
                    request,
                    "Order placed successfully with Cash on Delivery. Our team will contact you shortly.",
                )
                return redirect("order_success", order_number=order.order_number)

            if payment.gateway in ["esewa", "razorpay", "upi"]:
                # Redirect to central payment initialization
                return redirect(
                    reverse(
                        "initiate_payment", kwargs={"order_number": order.order_number}
                    )
                )
    else:
        initial = {}
        if request.user.is_authenticated:
            initial["full_name"] = (
                request.user.get_full_name() or request.user.username
            )
        form = CheckoutForm(initial=initial)

    return render(
        request,
        "orders/checkout.html",
        {"form": form, "cart": cart},
    )


@login_required
def order_success(request, order_number):
    order = get_object_or_404(
        Order, order_number=order_number, user=request.user
    )
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def order_failure(request, order_number):
    order = get_object_or_404(
        Order, order_number=order_number, user=request.user
    )
    return render(request, "orders/order_failure.html", {"order": order})


@login_required
def order_history(request):
    orders = request.user.orders.all()
    return render(request, "orders/order_history.html", {"orders": orders})

