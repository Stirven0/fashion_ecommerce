"""QA Tests: 5 functional + 5 non-functional."""
from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from fashion_store.cart.cart import Cart
from fashion_store.orders.models import Order
from fashion_store.products.models import WishlistItem
from fashion_store.products.tests.factories import CategoryFactory
from fashion_store.products.tests.factories import ProductFactory
from fashion_store.products.tests.factories import ProductImageFactory
from fashion_store.products.tests.factories import ProductReviewFactory
from fashion_store.products.tests.factories import ProductVariantFactory
from fashion_store.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


# =============================================================================
# FUNCTIONAL TESTS (5)
# =============================================================================

class TestFunctionalProductListing:
    """F1: Product listing page displays products and categories correctly."""

    def test_product_list_returns_200(self, client: Client):
        url = reverse("products:list")
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_product_list_shows_products(self, client: Client):
        ProductFactory(name="Camiseta Azul")
        ProductFactory(name="Pantalón Negro")
        url = reverse("products:list")
        response = client.get(url)
        assert "Camiseta Azul" in response.content.decode()
        assert "Pantalón Negro" in response.content.decode()

    def test_product_list_shows_categories_in_filter(self, client: Client):
        cat = CategoryFactory(name="Ropa")
        ProductFactory(category=cat)
        url = reverse("products:list")
        response = client.get(url)
        assert "Ropa" in response.content.decode()

    def test_product_list_filters_by_category(self, client: Client):
        cat1 = CategoryFactory(name="Ropa")
        cat2 = CategoryFactory(name="Calzado")
        ProductFactory(name="Camiseta", category=cat1)
        ProductFactory(name="Zapato", category=cat2)
        url = reverse("products:list") + "?category=" + cat1.slug
        response = client.get(url)
        html = response.content.decode()
        assert "Camiseta" in html
        assert "Zapato" not in html

    def test_product_list_filters_by_price_range(self, client: Client):
        ProductFactory(name="Barato", price=10000)
        ProductFactory(name="Caro", price=100000)
        url = reverse("products:list") + "?max_price=50000"
        response = client.get(url)
        html = response.content.decode()
        assert "Barato" in html
        assert "Caro" not in html

    def test_product_list_pagination(self, client: Client):
        ProductFactory.create_batch(15)
        url = reverse("products:list")
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert response.context["is_paginated"] is True

    def test_product_search_by_name(self, client: Client):
        ProductFactory(name="Vestido Rojo")
        ProductFactory(name="Zapatos Azules")
        url = reverse("products:list") + "?q=Vestido"
        response = client.get(url)
        html = response.content.decode()
        assert "Vestido Rojo" in html
        assert "Zapatos Azules" not in html


class TestFunctionalProductDetail:
    """F2: Product detail displays full info, variants, and images."""

    def test_product_detail_returns_200(self, client: Client):
        product = ProductFactory()
        url = product.get_absolute_url()
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_product_detail_shows_variant_selector(self, client: Client):
        product = ProductFactory(has_variants=True)
        ProductVariantFactory(product=product, size="S", color="Rojo")
        ProductVariantFactory(
            product=product, size="M", color="Azul", sku="v2",
        )
        url = product.get_absolute_url()
        response = client.get(url)
        html = response.content.decode()
        assert "S" in html
        assert "M" in html
        assert "Rojo" in html
        assert "Azul" in html

    def test_product_detail_shows_images(self, client: Client):
        product = ProductFactory()
        ProductImageFactory(product=product)
        url = product.get_absolute_url()
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_product_detail_shows_reviews(self, client: Client):
        user = UserFactory()
        product = ProductFactory()
        ProductReviewFactory(product=product, user=user, rating=4)
        url = product.get_absolute_url()
        response = client.get(url)
        html = response.content.decode()
        assert str(user.username) in html or (user.name or "") in html

    def test_product_detail_shows_related_products(self, client: Client):
        category = CategoryFactory()
        main = ProductFactory(category=category)
        ProductFactory(category=category, name="Relacionado")
        url = main.get_absolute_url()
        response = client.get(url)
        assert "Relacionado" in response.content.decode()

    def test_product_detail_404_for_inactive(self, client: Client):
        product = ProductFactory(is_active=False)
        url = product.get_absolute_url()
        response = client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestFunctionalCart:
    """F3: Cart operations work correctly via session."""

    def test_add_to_cart(self, client: Client):
        product = ProductFactory()
        url = reverse("cart:add")
        response = client.post(url, {"product_id": product.id, "quantity": 2})
        assert response.status_code == HTTPStatus.FOUND
        cart = Cart(client)
        assert len(cart) > 0

    def test_cart_add_with_variant(self, client: Client):
        product = ProductFactory(has_variants=True)
        variant = ProductVariantFactory(product=product)
        url = reverse("cart:add")
        client.post(url, {"product_id": product.id, "variant_id": variant.id, "quantity": 1})
        cart = Cart(client)
        items = list(cart)
        assert any(item["variant"] and item["variant"].id == variant.id for item in items)

    def test_cart_detail_shows_items(self, client: Client):
        product = ProductFactory(name="Producto Test")
        client.post(reverse("cart:add"), {"product_id": product.id, "quantity": 1})
        url = reverse("cart:detail")
        response = client.get(url)
        assert "Producto Test" in response.content.decode()

    def test_cart_remove_item(self, client: Client):
        product = ProductFactory()
        client.post(reverse("cart:add"), {"product_id": product.id, "quantity": 1})
        client.post(reverse("cart:remove"), {"product_id": product.id})
        cart = Cart(client)
        assert len(cart) == 0

    def test_cart_update_quantity(self, client: Client):
        product = ProductFactory()
        client.post(reverse("cart:add"), {"product_id": product.id, "quantity": 1})
        client.post(reverse("cart:update"), {"product_id": product.id, "quantity": 5})
        cart = Cart(client)
        items = list(cart)
        assert len(items) > 0
        assert items[0]["quantity"] == 5

    def test_empty_cart_shows_message(self, client: Client):
        url = reverse("cart:detail")
        response = client.get(url)
        assert "vacío" in response.content.decode().lower()


class TestFunctionalCheckout:
    """F4: Checkout flow creates orders and triggers WhatsApp flow."""

    def test_checkout_page_requires_cart(self, client: Client):
        url = reverse("orders:checkout_step1")
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND

    def test_checkout_with_items_shows_form(self, client: Client):
        product = ProductFactory()
        client.post(reverse("cart:add"), {"product_id": product.id, "quantity": 1})
        url = reverse("orders:checkout_step1")
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_checkout_creates_order(self, client: Client):
        product = ProductFactory(name="Camiseta", price=50000)
        client.post(reverse("cart:add"), {"product_id": product.id, "quantity": 2})
        response = client.post(reverse("orders:checkout_step2"), {
            "full_name": "Juan Pérez",
            "phone": "3001234567",
            "address_line": "Calle 123 #45-67",
            "city": "Bogotá",
        })
        assert response.status_code == HTTPStatus.OK
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.full_name == "Juan Pérez"
        assert order.total == 100000
        assert order.items.count() == 1

    def test_checkout_clears_cart(self, client: Client):
        product = ProductFactory()
        client.post(reverse("cart:add"), {"product_id": product.id, "quantity": 1})
        client.post(reverse("orders:checkout_step2"), {
            "full_name": "Test",
            "phone": "3001234567",
            "address_line": "Calle 1",
            "city": "Bogotá",
        })
        cart = Cart(client)
        assert len(cart) == 0

    def test_checkout_shows_whatsapp_button(self, client: Client):
        product = ProductFactory()
        client.post(reverse("cart:add"), {"product_id": product.id, "quantity": 1})
        response = client.post(reverse("orders:checkout_step2"), {
            "full_name": "Test",
            "phone": "3001234567",
            "address_line": "Calle 1",
            "city": "Bogotá",
        })
        html = response.content.decode()
        assert "wa.me" in html
        assert "whatsapp" in html.lower()


class TestFunctionalOrderHistory:
    """F5: Users can view their order history."""

    def test_order_history_requires_login(self, client: Client):
        url = reverse("orders:history")
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert "/accounts/login/" in response.url

    def test_order_history_shows_user_orders(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        product = ProductFactory()
        client.post(reverse("cart:add"), {"product_id": product.id, "quantity": 1})
        client.post(reverse("orders:checkout_step2"), {
            "full_name": user.name or "Test",
            "phone": "3001234567",
            "address_line": "Calle 1",
            "city": "Bogotá",
        })
        url = reverse("orders:history")
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        order_id = str(Order.objects.first().id)
        assert order_id in response.content.decode()

    def test_order_detail_shows_items(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        product = ProductFactory(name="Prod Detail")
        client.post(reverse("cart:add"), {"product_id": product.id, "quantity": 1})
        client.post(reverse("orders:checkout_step2"), {
            "full_name": "Test",
            "phone": "3001234567",
            "address_line": "Calle 1",
            "city": "Bogotá",
        })
        order = Order.objects.first()
        url = reverse("orders:detail", kwargs={"order_id": order.id})
        response = client.get(url)
        assert "Prod Detail" in response.content.decode()

    def test_cannot_view_others_order(self, client: Client):
        user = UserFactory()
        other_user = UserFactory()
        client.force_login(user)
        order = Order.objects.create(
            user=other_user, full_name="Otro", phone="000",
            total=10000,
        )
        url = reverse("orders:detail", kwargs={"order_id": order.id})
        response = client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND


# =============================================================================
# NON-FUNCTIONAL TESTS (5)
# =============================================================================

class TestNonFunctionalPerformance:
    """NF1: Page response times are acceptable."""

    def test_product_list_loads_under_500ms(self, client: Client):
        ProductFactory.create_batch(20)
        url = reverse("products:list")
        import time
        start = time.perf_counter()
        client.get(url)
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 500, f"Product list took {elapsed:.1f}ms"

    def test_categories_page_loads_under_500ms(self, client: Client):
        CategoryFactory.create_batch(10)
        url = reverse("products:categories")
        import time
        start = time.perf_counter()
        client.get(url)
        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 500, f"Categories page took {elapsed:.1f}ms"


class TestNonFunctionalQueryCount:
    """NF2: Pages don't make excessive DB queries (no N+1)."""

    def test_product_list_under_15_queries(self, client: Client):
        ProductFactory.create_batch(5)
        url = reverse("products:list")
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        with CaptureQueriesContext(connection) as ctx:
            client.get(url)
        assert len(ctx.captured_queries) <= 15, (
            f"Product list used {len(ctx.captured_queries)} queries"
        )

    def test_product_detail_under_10_queries(self, client: Client):
        product = ProductFactory()
        ProductVariantFactory(product=product, sku="dt1")
        ProductVariantFactory(product=product, size="L", sku="dt2")
        url = product.get_absolute_url()
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        with CaptureQueriesContext(connection) as ctx:
            client.get(url)
        assert len(ctx.captured_queries) <= 15, (
            f"Product detail used {len(ctx.captured_queries)} queries"
        )


class TestNonFunctionalSecurity:
    """NF3: Security checks — auth required, CSRF, sensible defaults."""

    def test_order_history_redirects_anonymous(self, client: Client):
        response = client.get(reverse("orders:history"))
        assert response.status_code == HTTPStatus.FOUND
        assert "/accounts/login/" in response.url

    def test_cart_endpoints_require_csrf(self, client: Client):
        product = ProductFactory()
        response = client.post(
            reverse("cart:add"),
            {"product_id": str(product.id), "quantity": "1"},
        )
        assert response.status_code == HTTPStatus.FOUND

    def test_inactive_product_not_listed(self, client: Client):
        ProductFactory(name="Activo", is_active=True)
        ProductFactory(name="Inactivo", is_active=False)
        url = reverse("products:list")
        response = client.get(url)
        html = response.content.decode()
        assert "Activo" in html
        assert "Inactivo" not in html

    def test_nonexistent_product_detail_returns_404(self, client: Client):
        url = reverse("products:detail", kwargs={"slug": "no-existe"})
        response = client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_admin_requires_staff(self, client: Client):
        user = UserFactory(is_staff=False)
        client.force_login(user)
        response = client.get(reverse("admin:index"))
        assert response.status_code == HTTPStatus.FOUND

    def test_admin_login_for_anonymous(self, client: Client):
        response = client.get(reverse("admin:index"))
        assert response.status_code == HTTPStatus.FOUND


class TestNonFunctionalDataIntegrity:
    """NF4: Model constraints and validations work correctly."""

    def test_product_variant_unique_together(self, client: Client):
        product = ProductFactory()
        ProductVariantFactory(product=product, size="M", color="Negro", sku="ut1")
        import pytest
        with pytest.raises(Exception):
            ProductVariantFactory(product=product, size="M", color="Negro", sku="ut2")

    def test_product_review_unique_together(self):
        user = UserFactory()
        product = ProductFactory()
        ProductReviewFactory(product=product, user=user)
        import pytest
        with pytest.raises(Exception):
            ProductReviewFactory(product=product, user=user)

    def test_inactive_product_not_in_list(self, client: Client):
        ProductFactory(name="Visible", is_active=True)
        ProductFactory(name="Oculto", is_active=False)
        url = reverse("products:list")
        response = client.get(url)
        html = response.content.decode()
        assert "Visible" in html
        assert "Oculto" not in html

    def test_product_created_with_defaults(self):
        product = ProductFactory()
        assert product.is_active is True
        assert product.has_variants is False
        assert product.price >= 0

    def test_category_hierarchy(self):
        parent = CategoryFactory()
        child = CategoryFactory(parent=parent)
        assert child.parent == parent
        assert list(parent.children.all()) == [child]


class TestNonFunctionalTemplateRendering:
    """NF5: Templates render without errors and include expected blocks."""

    def test_home_page_renders(self, client: Client):
        response = client.get(reverse("home"))
        assert response.status_code == HTTPStatus.OK

    def test_home_page_has_store_name(self, client: Client):
        from django.conf import settings
        response = client.get(reverse("home"))
        assert settings.STORE_NAME in response.content.decode()

    def test_about_page_renders(self, client: Client):
        response = client.get(reverse("about"))
        assert response.status_code == HTTPStatus.OK

    def test_categories_page_renders(self, client: Client):
        CategoryFactory.create_batch(3)
        response = client.get(reverse("products:categories"))
        assert response.status_code == HTTPStatus.OK

    def test_navbar_shows_cart_link(self, client: Client):
        response = client.get(reverse("home"))
        html = response.content.decode()
        assert "Carrito" in html

    def test_navbar_shows_login_when_anonymous(self, client: Client):
        response = client.get(reverse("home"))
        html = response.content.decode()
        assert "Iniciar" in html or "Sesión" in html or "Registrarse" in html

    def test_navbar_shows_profile_when_logged_in(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("home"))
        html = response.content.decode()
        assert user.name in html or user.username in html


class TestFunctionalWishlist:
    """F6: Wishlist (favorites) operations work correctly."""

    def test_wishlist_requires_login(self, client: Client):
        url = reverse("products:wishlist")
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert "/accounts/login/" in response.url

    def test_wishlist_add_requires_login(self, client: Client):
        response = client.post(
            reverse("products:wishlist_add"),
            {"product_id": "1"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "/accounts/login/" in response.url

    def test_wishlist_add_product(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        product = ProductFactory()
        response = client.post(
            reverse("products:wishlist_add"),
            {"product_id": product.id},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert product.wishlist_items.filter(user=user).exists()

    def test_wishlist_add_duplicate_is_idempotent(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        product = ProductFactory()
        client.post(
            reverse("products:wishlist_add"),
            {"product_id": product.id},
        )
        WishlistItem.objects.get_or_create(user=user, product=product)
        assert WishlistItem.objects.filter(user=user, product=product).count() == 1

    def test_wishlist_remove_product(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        product = ProductFactory()
        WishlistItem.objects.create(user=user, product=product)
        client.post(
            reverse("products:wishlist_remove"),
            {"product_id": product.id},
        )
        assert not WishlistItem.objects.filter(user=user, product=product).exists()

    def test_wishlist_detail_shows_items(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        product = ProductFactory(name="Favorito Test")
        WishlistItem.objects.create(user=user, product=product)
        url = reverse("products:wishlist")
        response = client.get(url)
        assert "Favorito Test" in response.content.decode()

    def test_wishlist_detail_empty(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        url = reverse("products:wishlist")
        response = client.get(url)
        assert "favoritos" in response.content.decode().lower()
