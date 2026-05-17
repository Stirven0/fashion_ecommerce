from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from fashion_store.products.models import Category
from fashion_store.products.models import Product
from fashion_store.products.models import ProductImage
from fashion_store.products.models import ProductReview
from fashion_store.products.models import ProductVariant


class CategoryFactory(DjangoModelFactory[Category]):
    name = factory.Faker("word")
    slug = factory.Faker("slug")
    is_active = True

    class Meta:
        model = Category
        django_get_or_create = ["slug"]


class ProductFactory(DjangoModelFactory[Product]):
    category = factory.SubFactory(CategoryFactory)
    name = factory.Faker("sentence", nb_words=3)
    slug = factory.Faker("slug")
    price = 50000

    class Meta:
        model = Product
        django_get_or_create = ["slug"]


class ProductVariantFactory(DjangoModelFactory[ProductVariant]):
    product = factory.SubFactory(ProductFactory)
    size = "M"
    color = "Negro"
    sku = factory.Sequence(lambda n: f"sku-{n}")
    stock = 10
    is_active = True

    class Meta:
        model = ProductVariant


class ProductImageFactory(DjangoModelFactory[ProductImage]):
    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(color="blue")

    class Meta:
        model = ProductImage


class ProductReviewFactory(DjangoModelFactory[ProductReview]):
    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory("fashion_store.users.tests.factories.UserFactory")
    rating = 5
    comment = factory.Faker("sentence")

    class Meta:
        model = ProductReview
