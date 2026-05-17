from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from fashion_store.cart.cart import Cart

from .forms import CheckoutForm
from .models import Order
from .models import OrderItem
from .models import ShippingAddress


def checkout_step1(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Tu carrito está vacío")
        return redirect("cart:detail")

    form = CheckoutForm()
    if request.user.is_authenticated:
        last_address = ShippingAddress.objects.filter(user=request.user).last()
        if last_address:
            form = CheckoutForm(
                initial={
                    "full_name": last_address.full_name,
                    "phone": last_address.phone,
                    "address_line": last_address.address_line,
                    "city": last_address.city,
                    "department": last_address.department,
                    "notes": last_address.notes,
                },
            )

    return render(
        request,
        "orders/checkout_step1.html",
        {
            "cart": cart,
            "form": form,
            "store_whatsapp": settings.STORE_WHATSAPP,
        },
    )


def checkout_step2(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            shipping = form.save(commit=False)
            if request.user.is_authenticated:
                shipping.user = request.user
            shipping.save()

            full_name = form.cleaned_data["full_name"]
            phone = form.cleaned_data["phone"]
            email = form.cleaned_data.get("email", "")
            notes = form.cleaned_data.get("notes", "")

            total = cart.get_total_price()

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                phone=phone,
                email=email,
                notes=notes,
                total=total,
                shipping_address=shipping,
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    variant=item["variant"],
                    product_name=item["product"].name,
                    variant_info=(
                        f"{item['variant'].size} / {item['variant'].color}"
                        if item["variant"]
                        else ""
                    ),
                    quantity=item["quantity"],
                    price=item["price"],
                )

            cart.clear()

            whatsapp_number = settings.STORE_WHATSAPP
            store_name = settings.STORE_NAME
            items_text = "\n".join(
                f"• {item['product_name']} ({item['variant_info']}) "
                f"x{item['quantity']} = "
                f"${item['price'] * item['quantity']:,.0f}"
                for item in order.items.values(
                    "product_name",
                    "variant_info",
                    "quantity",
                    "price",
                )
            )

            message = (
                f"¡Hola {store_name}! 👋\n\n"
                f"Quiero hacer el siguiente pedido:\n\n"
                f"📦 *Pedido #{order.id}*\n"
                f"{items_text}\n\n"
                f"💰 *Total: ${order.total:,.0f}*\n\n"
                f"👤 *Datos de envío:*\n"
                f"Nombre: {full_name}\n"
                f"Teléfono: {phone}\n"
                f"Dirección: {shipping.address_line}, {shipping.city}\n"
                f"Notas: {notes or 'Ninguna'}\n\n"
                f"¡Gracias! 🙌"
            )

            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={quote(message)}"

            return render(
                request,
                "orders/checkout_confirm.html",
                {
                    "order": order,
                    "whatsapp_url": whatsapp_url,
                },
            )

    return redirect("orders:checkout_step1")


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "orders/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})
