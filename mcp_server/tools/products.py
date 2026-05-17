# ruff: noqa: FBT001, FBT002, PLR0913
from django.db.models import Sum
from django.utils.text import slugify

from fashion_store.orders.models import OrderItem
from fashion_store.products.models import Category
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


def _make_slug(name: str) -> str:
    slug = slugify(name)
    if not slug:
        slug = "producto"
    original = slug
    counter = 1
    while Product.objects.filter(slug=slug).exists():
        slug = f"{original}-{counter}"
        counter += 1
    return slug


def add_product(
    category_id: int,
    name: str,
    price: float,
    description: str = "",
    compare_price: float | None = None,
    has_variants: bool = False,
    is_active: bool = True,
) -> dict:
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return {"error": f"Category with id={category_id} does not exist"}

    slug = _make_slug(name)

    product = Product.objects.create(
        category=category,
        name=name.strip(),
        slug=slug,
        description=description.strip(),
        price=price,
        compare_price=compare_price,
        has_variants=has_variants,
        is_active=is_active,
    )
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "price": int(product.price),
        "compare_price": int(product.compare_price) if product.compare_price else None,
        "description": product.description,
        "category": category.name,
        "has_variants": product.has_variants,
        "is_active": product.is_active,
        "url": product.get_absolute_url(),
    }


def add_product_variant(
    product_id: int,
    size: str = "",
    color: str = "",
    color_code: str = "",
    stock: int = 0,
    price_override: float | None = None,
    sku: str = "",
    is_active: bool = True,
) -> dict:
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return {"error": f"Product with id={product_id} does not exist"}

    variant = ProductVariant.objects.create(
        product=product,
        size=size.strip(),
        color=color.strip(),
        color_code=color_code.strip(),
        stock=stock,
        price_override=price_override,
        sku=sku.strip(),
        is_active=is_active,
    )
    return {
        "id": variant.id,
        "product_id": product.id,
        "product_name": product.name,
        "size": variant.size or "-",
        "color": variant.color or "-",
        "stock": variant.stock,
        "price_override": (
            int(variant.price_override) if variant.price_override else None
        ),
        "sku": variant.sku,
        "is_active": variant.is_active,
    }
