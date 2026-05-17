from django.views.generic import TemplateView

from fashion_store.products.models import Category
from fashion_store.products.models import Product


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(
            parent__isnull=True,
            is_active=True,
        )
        context["featured_products"] = Product.objects.filter(is_active=True)[:8]
        return context
