from django.urls import path

from .views import (
    OrderListView, OrderDetailView,
    create_order, cancel_order,
    admin_order_list, update_order_status
)

urlpatterns = [
    # Customer endpoints
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', create_order, name='order-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/cancel/', cancel_order, name='order-cancel'),
    
    # Admin endpoints
    path('admin/all/', admin_order_list, name='admin-order-list'),
    path('admin/<int:order_id>/status/', update_order_status, name='admin-order-status'),
]

