from django.urls import path

from .views import (
    calculate_shipping, ShipmentListView, ShipmentDetailView,
    create_shipment, update_shipment_tracking, track_shipment
)

urlpatterns = [
    path('calculate/', calculate_shipping, name='shipping-calculate'),
    path('shipments/', ShipmentListView.as_view(), name='shipment-list'),
    path('shipments/<int:pk>/', ShipmentDetailView.as_view(), name='shipment-detail'),
    path('shipments/create/', create_shipment, name='shipment-create'),
    path('shipments/<int:shipment_id>/tracking/', update_shipment_tracking, name='shipment-tracking'),
    path('track/<str:tracking_number>/', track_shipment, name='track-shipment'),
]
