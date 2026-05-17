from django.db.models import Sum

from fashion_store.orders.models import OrderItem
from fashion_store.products.models import Product
from fashion_store.products.models import ProductVariant


def get_best_sellers(limit: int = 10) -> list[dict]:
    items = (
        OrderItem.objects.values("product_name", "product_id")
        .annotate(total_qty=Sum("quantity"), total_revenue=Sum("price"))
        .order_by("-total_qty")[:limit]
    )
    return [
        {
            "product_name": item["product_name"],
            "product_id": item["product_id"],
            "units_sold": item["total_qty"],
            "total_revenue": int(item["total_revenue"] or 0),
        }
        for item in items
    ]


def get_low_stock(threshold: int = 5) -> list[dict]:
    variants = (
        ProductVariant.objects.filter(
            stock__lte=threshold,
            is_active=True,
        )
        .select_related("product")
        .order_by("stock")
    )
    return [
        {
            "variant_id": v.id,
            "product_id": v.product_id,
            "product_name": v.product.name,
            "size": v.size or "-",
            "color": v.color or "-",
            "stock": v.stock,
            "is_out_of_stock": v.stock == 0,
        }
        for v in variants
    ]


def search_products(query: str) -> list[dict]:
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True,
    )[:20]
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": int(p.price),
            "category": p.category.name,
            "slug": p.slug,
            "has_variants": p.has_variants,
            "url": p.get_absolute_url(),
        }
        for p in products
    ]


def get_product_detail(product_id: int) -> dict | None:
    try:
        p = (
            Product.objects.select_related("category")
            .prefetch_related(
                "variants",
                "images",
            )
            .get(id=product_id)
        )
    except Product.DoesNotExist:
        return None

    variants = [
        {
            "id": v.id,
            "size": v.size or "-",
            "color": v.color or "-",
            "stock": v.stock,
            "price_override": int(v.price_override) if v.price_override else None,
            "sku": v.sku,
            "is_active": v.is_active,
        }
        for v in p.variants.all()
    ]

    return {
        "id": p.id,
        "name": p.name,
        "price": int(p.price),
        "compare_price": int(p.compare_price) if p.compare_price else None,
        "description": p.description,
        "category": p.category.name,
        "is_active": p.is_active,
        "has_variants": p.has_variants,
        "total_variants": len(variants),
        "total_stock": sum(v["stock"] for v in variants) if variants else 0,
        "variants": variants,
        "created_at": p.created_at.isoformat(),
    }
