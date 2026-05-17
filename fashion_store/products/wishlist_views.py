from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import Product
from .models import WishlistItem


@require_POST
@login_required
def wishlist_add(request):
    product_id = request.POST.get("product_id")
    product = get_object_or_404(Product, id=product_id, is_active=True)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.name} agregado a favoritos")
    return redirect(product.get_absolute_url())


@require_POST
@login_required
def wishlist_remove(request):
    product_id = request.POST.get("product_id")
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    messages.success(request, "Producto eliminado de favoritos")
    return redirect("products:wishlist")


@login_required
def wishlist_detail(request):
    items = WishlistItem.objects.filter(user=request.user).select_related("product")
    return render(
        request,
        "products/wishlist_detail.html",
        {"wishlist_items": items},
    )
