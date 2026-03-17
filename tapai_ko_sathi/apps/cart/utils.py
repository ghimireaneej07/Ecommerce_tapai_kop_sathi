from .models import Cart


def attach_cart_to_user(request, user):
    """
    When a user logs in or signs up, bind any existing session cart to them.
    This keeps carts consistent across devices and sessions.
    """
    if not hasattr(request, "session"):
        return
    session_key = request.session.session_key
    if not session_key:
        return
    try:
        session_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)
    if session_cart.id == user_cart.id:
        return

    for item in session_cart.items.select_related("product"):
        existing = user_cart.items.filter(product=item.product).first()
        if existing:
            existing.quantity += item.quantity
            existing.save(update_fields=["quantity"])
        else:
            item.cart = user_cart
            item.save(update_fields=["cart"])

    session_cart.delete()

