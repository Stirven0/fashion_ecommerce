from .cart import Cart


def cart_items(request):
    if request.user.is_authenticated or not request.user.is_anonymous:
        cart = Cart(request)
        return {"cart_items_count": len(cart), "cart": cart}
    return {"cart_items_count": 0, "cart": None}
