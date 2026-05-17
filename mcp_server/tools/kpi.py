from collections import defaultdict
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from fashion_store.orders.models import Order
from fashion_store.orders.models import OrderItem
from fashion_store.products.models import Product
from fashion_store.products.models import ProductVariant


def get_kpis() -> dict:
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(
        status__in=["pending_whatsapp", "confirmed"],
    ).count()
    total_revenue = (
        Order.objects.filter(status="delivered").aggregate(s=Sum("total"))["s"] or 0
    )
    low_stock_count = ProductVariant.objects.filter(
        stock__lte=5,
        is_active=True,
    ).count()
    out_of_stock = ProductVariant.objects.filter(
        stock=0,
        is_active=True,
    ).count()

    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": total_products - active_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_revenue": int(total_revenue),
        "low_stock_variants": low_stock_count,
        "out_of_stock_variants": out_of_stock,
    }


def get_revenue_trend(days: int = 7) -> list[dict]:
    today = timezone.now().date()
    revenue_by_day: defaultdict[str, int] = defaultdict(int)
    for i in range(days):
        day = today - timedelta(days=i)
        day_total = (
            OrderItem.objects.filter(
                order__status="delivered",
                order__created_at__date=day,
            ).aggregate(s=Sum("price"))["s"]
            or 0
        )
        revenue_by_day[day.isoformat()] = int(day_total)
    return [
        {"date": day, "revenue": amount}
        for day, amount in sorted(revenue_by_day.items())
    ]
