from django.urls import path

from .views import (
    InventoryLocationListView, InventoryListView,
    InventoryMovementListView, update_stock, check_stock, reserve_items
)

urlpatterns = [
    path('locations/', InventoryLocationListView.as_view(), name='inventory-locations'),
    path('stock/', InventoryListView.as_view(), name='inventory-list'),
    path('movements/', InventoryMovementListView.as_view(), name='inventory-movements'),
    path('update/', update_stock, name='inventory-update'),
    path('check/<int:variant_id>/', check_stock, name='inventory-check'),
    path('reserve/', reserve_items, name='inventory-reserve'),
]

