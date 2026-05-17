from collections import defaultdict
from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from fashion_store.orders.models import Order
from fashion_store.orders.models import OrderItem
from fashion_store.products.models import Category
from fashion_store.products.models import Product
from fashion_store.products.models import ProductVariant

from .forms import DashboardProductForm
from .forms import DashboardVariantFormSet


@method_decorator(staff_member_required(login_url="admin:login"), name="dispatch")
class DashboardHomeView(TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

        context["total_products"] = total_products
        context["active_products"] = active_products
        context["inactive_products"] = total_products - active_products
        context["total_orders"] = total_orders
        context["pending_orders"] = pending_orders
        context["total_revenue"] = total_revenue
        context["low_stock_count"] = low_stock_count

        context["best_sellers"] = (
            OrderItem.objects.values("product_name")
            .annotate(total_qty=Sum("quantity"))
            .order_by("-total_qty")[:10]
        )

        context["low_stock_variants"] = (
            ProductVariant.objects.filter(stock__lte=5, is_active=True)
            .select_related("product")
            .order_by("stock")[:10]
        )

        context["recent_orders"] = Order.objects.select_related(
            "shipping_address",
        ).order_by("-created_at")[:10]

        today = timezone.now().date()
        revenue_by_day = defaultdict(int)
        for i in range(7):
            day = today - timedelta(days=i)
            day_total = (
                OrderItem.objects.filter(
                    order__status="delivered",
                    order__created_at__date=day,
                ).aggregate(s=Sum("price"))["s"]
                or 0
            )
            revenue_by_day[day.isoformat()] = int(day_total)

        context["revenue_by_day"] = dict(sorted(revenue_by_day.items()))

        return context


@method_decorator(staff_member_required(login_url="admin:login"), name="dispatch")
class DashboardProductListView(ListView):
    model = Product
    template_name = "dashboard/product_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.select_related("category").annotate(
            total_sold=Sum("orderitem__quantity"),
        )
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        cat = self.request.GET.get("category")
        if cat:
            qs = qs.filter(category_id=cat)
        status = self.request.GET.get("status")
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["current_q"] = self.request.GET.get("q", "")
        context["current_cat"] = self.request.GET.get("category", "")
        context["current_status"] = self.request.GET.get("status", "")
        return context


@method_decorator(staff_member_required(login_url="admin:login"), name="dispatch")
class DashboardProductCreateView(CreateView):
    model = Product
    form_class = DashboardProductForm
    template_name = "dashboard/product_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["variant_formset"] = DashboardVariantFormSet(
                self.request.POST,
                self.request.FILES,
            )
        else:
            context["variant_formset"] = DashboardVariantFormSet()
        context["title"] = "Crear producto"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        variant_formset = context["variant_formset"]
        if variant_formset.is_valid():
            self.object = form.save()
            variant_formset.instance = self.object
            variant_formset.save()
            messages.success(self.request, "Producto creado exitosamente")
            return redirect("dashboard:product_list")
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(staff_member_required(login_url="admin:login"), name="dispatch")
class DashboardProductUpdateView(UpdateView):
    model = Product
    form_class = DashboardProductForm
    template_name = "dashboard/product_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["variant_formset"] = DashboardVariantFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
            )
        else:
            context["variant_formset"] = DashboardVariantFormSet(
                instance=self.object,
            )
        context["title"] = f"Editar: {self.object.name}"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        variant_formset = context["variant_formset"]
        if variant_formset.is_valid():
            self.object = form.save()
            variant_formset.instance = self.object
            variant_formset.save()
            messages.success(self.request, "Producto actualizado exitosamente")
            return redirect("dashboard:product_list")
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


@require_POST
@staff_member_required(login_url="admin:login")
def dashboard_product_toggle_active(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    status = "activado" if product.is_active else "desactivado"
    messages.success(request, f"{product.name} {status}")
    return redirect("dashboard:product_list")


@method_decorator(staff_member_required(login_url="admin:login"), name="dispatch")
class DashboardOrderListView(ListView):
    model = Order
    template_name = "dashboard/order_list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        qs = Order.objects.select_related("shipping_address").order_by("-created_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                full_name__icontains=q,
            ) | qs.filter(
                phone__icontains=q,
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_status"] = self.request.GET.get("status", "")
        context["current_q"] = self.request.GET.get("q", "")
        context["statuses"] = Order.STATUS_CHOICES
        return context


@method_decorator(staff_member_required(login_url="admin:login"), name="dispatch")
class DashboardOrderDetailView(DetailView):
    model = Order
    template_name = "dashboard/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.select_related("shipping_address").prefetch_related(
            "items",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Order.STATUS_CHOICES
        return context


@require_POST
@staff_member_required(login_url="admin:login")
def dashboard_order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get("status")
    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
    if new_status in valid_statuses:
        order.status = new_status
        order.save(update_fields=["status"])
        msg = f"Pedido #{order.id} actualizado a {order.get_status_display()}"
        messages.success(request, msg)
    return redirect("dashboard:order_detail", pk=order.pk)
