from django.contrib import admin

from .models import Order
from .models import OrderItem
from .models import ShippingAddress


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = [
        "product",
        "variant",
        "product_name",
        "variant_info",
        "quantity",
        "price",
    ]
    extra = 0
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "phone", "status", "total", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["full_name", "phone", "email"]
    inlines = [OrderItemInline]
    readonly_fields = ["total", "created_at", "updated_at"]
    actions = ["mark_confirmed", "mark_shipped", "mark_delivered", "mark_cancelled"]

    def mark_confirmed(self, request, queryset):
        queryset.update(status="confirmed")

    mark_confirmed.short_description = "Marcar como confirmados"

    def mark_shipped(self, request, queryset):
        queryset.update(status="shipped")

    mark_shipped.short_description = "Marcar como enviados"

    def mark_delivered(self, request, queryset):
        queryset.update(status="delivered")

    mark_delivered.short_description = "Marcar como entregados"

    def mark_cancelled(self, request, queryset):
        queryset.update(status="cancelled")

    mark_cancelled.short_description = "Marcar como cancelados"


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone", "city", "created_at"]
    search_fields = ["full_name", "phone"]


admin.site.register(OrderItem)
