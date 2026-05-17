from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from fashion_store.products.models import Product
from fashion_store.products.models import ProductVariant

from .cart import Cart


@require_POST
def cart_add(request):
    cart = Cart(request)
    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")
    quantity = int(request.POST.get("quantity", 1))

    product = get_object_or_404(Product, id=product_id, is_active=True)
    if (
        variant_id
        and not ProductVariant.objects.filter(
            id=variant_id,
            is_active=True,
        ).exists()
    ):
        messages.error(request, "Variante no disponible")
        return redirect(product.get_absolute_url())

    cart.add(product_id=product_id, variant_id=variant_id, quantity=quantity)
    messages.success(request, f"{product.name} agregado al carrito")
    return redirect("cart:detail")


@require_POST
def cart_remove(request):
    cart = Cart(request)
    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")
    cart.remove(product_id=product_id, variant_id=variant_id)
    messages.success(request, "Producto eliminado del carrito")
    return redirect("cart:detail")


@require_POST
def cart_update(request):
    cart = Cart(request)
    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")
    quantity = int(request.POST.get("quantity", 1))
    cart.add(
        product_id=product_id,
        variant_id=variant_id,
        quantity=quantity,
        override_quantity=True,
    )
    messages.success(request, "Carrito actualizado")
    return redirect("cart:detail")


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/cart_detail.html", {"cart": cart})
