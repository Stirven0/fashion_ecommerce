from django.db.models import Min
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView

from .models import Category
from .models import Product


class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        category_slug = self.request.GET.get("category")
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            children = category.children.filter(is_active=True)
            category_ids = [category.id] + [c.id for c in children]
            queryset = queryset.filter(category_id__in=category_ids)

        size = self.request.GET.get("size")
        if size:
            queryset = queryset.filter(
                variants__size=size,
                variants__is_active=True,
            ).distinct()

        color = self.request.GET.get("color")
        if color:
            queryset = queryset.filter(
                variants__color=color,
                variants__is_active=True,
            ).distinct()

        min_price = self.request.GET.get("min_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self.request.GET.get("max_price")
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q),
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(
            parent__isnull=True,
            is_active=True,
        )
        context["sizes"] = (
            Product.objects.filter(is_active=True)
            .exclude(variants__size="")
            .values_list("variants__size", flat=True)
            .distinct()
            .order_by("variants__size")
        )
        context["colors"] = (
            Product.objects.filter(is_active=True)
            .exclude(variants__color="")
            .values_list("variants__color", flat=True)
            .distinct()
            .order_by("variants__color")
        )
        price_range = Product.objects.filter(is_active=True).aggregate(
            min=Min("price"),
        )
        context["price_min"] = price_range["min"] or 0
        context["current_category"] = self.request.GET.get("category", "")
        return context


class CategoryListView(ListView):
    model = Category
    template_name = "products/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True, is_active=True)


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        active_variants = product.variants.filter(is_active=True)
        sizes = []
        colors = []
        for v in active_variants:
            if v.size and v.size not in sizes:
                sizes.append(v.size)
            if v.color and v.color not in colors:
                colors.append(v.color)

        context["sizes"] = sizes
        context["colors"] = colors
        context["variants_json"] = list(
            active_variants.values(
                "id",
                "size",
                "color",
                "color_code",
                "stock",
                "price_override",
            ),
        )
        context["related_products"] = Product.objects.filter(
            category=product.category,
            is_active=True,
        ).exclude(id=product.id)[:4]
        return context
