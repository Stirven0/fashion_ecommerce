from django.db.models import Sum

from fashion_store.orders.models import Order
from fashion_store.orders.models import OrderItem
from fashion_store.products.models import Product
from fashion_store.products.models import ProductVariant

from .kpi import get_kpis
from .kpi import get_revenue_trend
from .orders import get_pending_orders
from .products import get_best_sellers
from .products import get_low_stock


def get_sales_suggestions() -> list[dict]:
    suggestions = []

    total_orders = Order.objects.count()
    if total_orders == 0:
        msg = (
            "No hay pedidos registrados. Revisa que el checkout "
            "funcione correctamente y promociona la tienda."
        )
        suggestions.append(
            {
                "type": "warning",
                "area": "ventas",
                "message": msg,
            },
        )
        return suggestions

    out_of_stock = ProductVariant.objects.filter(stock=0, is_active=True)
    if out_of_stock.exists():
        names_list = out_of_stock.values_list("product__name", flat=True).distinct()[:5]
        names = ", ".join(names_list)
        suggestions.append(
            {
                "type": "critical",
                "area": "inventario",
                "message": f"Productos agotados: {names}. Considera reabastecer.",
            },
        )

    low_stock = ProductVariant.objects.filter(
        stock__lte=5,
        stock__gt=0,
        is_active=True,
    )
    if low_stock.exists():
        count = low_stock.count()
        suggestions.append(
            {
                "type": "warning",
                "area": "inventario",
                "message": f"{count} variantes con stock bajo (≤5 uds).",
            },
        )

    inactive_products = Product.objects.filter(is_active=False)
    if inactive_products.exists():
        count = inactive_products.count()
        suggestions.append(
            {
                "type": "info",
                "area": "productos",
                "message": f"Tienes {count} productos inactivos. ¿Revisarlos?",
            },
        )

    pending = Order.objects.filter(status="pending_whatsapp")
    if pending.exists():
        msg = f"{pending.count()} pedido(s) esperando confirmación WhatsApp."
        suggestions.append(
            {
                "type": "warning",
                "area": "pedidos",
                "message": msg,
            },
        )

    best = (
        OrderItem.objects.values("product_name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")
        .first()
    )
    if best and best["total_qty"] > 0:
        suggestions.append(
            {
                "type": "info",
                "area": "ventas",
                "message": (
                    f"'{best['product_name']}' es el más vendido "
                    f"({best['total_qty']} uds). "
                    "Destácalo en la portada."
                ),
            },
        )

    never_sold = Product.objects.filter(
        is_active=True,
        orderitem__isnull=True,
    ).count()
    if never_sold > 0:
        suggestions.append(
            {
                "type": "info",
                "area": "productos",
                "message": (
                    f"{never_sold} producto(s) activos nunca se han vendido. "
                    "Revisa si necesitan mejor descripción, precio o fotos."
                ),
            },
        )

    return suggestions


def get_full_report() -> dict:
    return {
        "kpis": get_kpis(),
        "revenue_trend": get_revenue_trend(7),
        "pending_orders": get_pending_orders(),
        "best_sellers": get_best_sellers(5),
        "low_stock": get_low_stock(5),
        "suggestions": get_sales_suggestions(),
    }
