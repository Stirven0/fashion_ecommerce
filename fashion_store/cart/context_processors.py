from .cart import Cart


def cart_items(request):
    cart = Cart(request)
    return {"cart_items_count": len(cart), "cart": cart}
