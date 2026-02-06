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
        cart = Cart.objects.get(session_key=session_key, user__isnull=True)
    except Cart.DoesNotExist:
        return
    cart.user = user
    cart.save()

