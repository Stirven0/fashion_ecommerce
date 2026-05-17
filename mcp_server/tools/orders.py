from fashion_store.orders.models import Order


def get_pending_orders() -> list[dict]:
    orders = (
        Order.objects.filter(
            status="pending_whatsapp",
        )
        .select_related("shipping_address")
        .order_by("-created_at")
    )
    return [
        {
            "id": o.id,
            "customer": o.full_name,
            "phone": o.phone,
            "total": int(o.total),
            "status": o.status,
            "status_label": o.get_status_display(),
            "items_count": o.items.count(),
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]


def get_orders_by_status(status: str | None = None) -> list[dict]:
    qs = Order.objects.select_related("shipping_address").order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    return [
        {
            "id": o.id,
            "customer": o.full_name,
            "phone": o.phone,
            "total": int(o.total),
            "status": o.status,
            "status_label": o.get_status_display(),
            "created_at": o.created_at.isoformat(),
        }
        for o in qs[:50]
    ]


def get_recent_orders(limit: int = 10) -> list[dict]:
    orders = Order.objects.select_related(
        "shipping_address",
    ).order_by("-created_at")[:limit]
    return [
        {
            "id": o.id,
            "customer": o.full_name,
            "phone": o.phone,
            "total": int(o.total),
            "status": o.status,
            "status_label": o.get_status_display(),
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]
