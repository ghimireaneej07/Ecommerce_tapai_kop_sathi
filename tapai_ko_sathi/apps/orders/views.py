import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from tapai_ko_sathi.apps.cart.models import Cart
from tapai_ko_sathi.apps.orders.forms import CheckoutForm
from tapai_ko_sathi.apps.orders.models import Order, OrderItem
from tapai_ko_sathi.apps.payments.models import Payment


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
    return f"TKS-{uuid.uuid4().hex[:10].upper()}"


@login_required
def checkout_start(request):
    cart = _get_user_cart(request)
    if not cart or cart.total_items == 0:
        messages.info(request, "Your cart is empty.")
        return redirect("cart_page")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order_number = _generate_order_number()
            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                status="pending",
                payment_method=form.cleaned_data["payment_method"],
                total_amount=cart.total_price,
                full_name=form.cleaned_data["full_name"],
                phone=form.cleaned_data["phone"],
                address_line1=form.cleaned_data["address_line1"],
                address_line2=form.cleaned_data["address_line2"],
                city=form.cleaned_data["city"],
                postal_code=form.cleaned_data["postal_code"],
            )

            # Copy cart items into order
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )

            payment = Payment.objects.create(
                order=order,
                gateway=form.cleaned_data["payment_method"],
                amount=order.total_amount,
                status="initiated",
            )

            # Clear cart after creating order; for online payments, status is updated after verification
            cart.items.all().delete()

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

