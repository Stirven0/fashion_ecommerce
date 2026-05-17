from decimal import Decimal

from django.conf import settings

from fashion_store.products.models import Product
from fashion_store.products.models import ProductVariant


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(
        self,
        product_id,
        variant_id=None,
        quantity=1,
        override_quantity=False,  # noqa: FBT002
    ):
        product_id = str(product_id)
        variant_id = str(variant_id) if variant_id else None
        key = f"{product_id}_{variant_id}" if variant_id else product_id

        if key not in self.cart:
            self.cart[key] = {
                "product_id": product_id,
                "variant_id": variant_id,
                "quantity": 0,
            }

        if override_quantity:
            self.cart[key]["quantity"] = quantity
        else:
            self.cart[key]["quantity"] += quantity

        self.save()

    def remove(self, product_id, variant_id=None):
        product_id = str(product_id)
        variant_id = str(variant_id) if variant_id else None
        key = f"{product_id}_{variant_id}" if variant_id else product_id

        if key in self.cart:
            del self.cart[key]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def __iter__(self):
        for item in self.cart.values():
            product = Product.objects.filter(
                id=item["product_id"],
                is_active=True,
            ).first()
            if not product:
                continue
            variant = None
            if item["variant_id"]:
                variant = ProductVariant.objects.filter(
                    id=item["variant_id"],
                    is_active=True,
                ).first()
            price = (
                variant.price_override
                if variant and variant.price_override
                else product.price
            )
            item["product"] = product
            item["variant"] = variant
            item["price"] = price
            item["total"] = Decimal(price) * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        total = Decimal(0)
        for item in self:
            total += item["total"]
        return total

    def get_items(self):
        return list(self.cart.values())
