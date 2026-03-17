from .models import Cart


def _get_or_create_cart(request):
    """
    Helper to fetch the current cart for the user/session.
    Lightweight and safe to use in a context processor.
    """
    if not hasattr(request, "session"):
        return None

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={"session_key": session_key},
        )
        if not created and cart.session_key != session_key:
            cart.session_key = session_key
            cart.save(update_fields=["session_key"])
        return cart

    cart, _ = Cart.objects.get_or_create(
        user=None,
        session_key=session_key,
    )
    return cart


def cart_summary(request):
    """
    Expose cart info to all templates (used in header/cart icon).
    """
    cart = _get_or_create_cart(request)
    if not cart:
        return {"cart_item_count": 0, "cart_total_price": 0}
    return {
        "cart_item_count": cart.total_items,
        "cart_total_price": cart.total_price,
    }

