from rest_framework import serializers

from .models import Shipment, ShipmentItem, ShippingRate


class ShipmentItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='order_item.product_name', read_only=True)
    sku = serializers.CharField(source='order_item.sku', read_only=True)
    
    class Meta:
        model = ShipmentItem
        fields = ['order_item', 'sku', 'product_name', 'quantity']


class ShipmentSerializer(serializers.ModelSerializer):
    items = ShipmentItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    carrier_display = serializers.CharField(source='get_carrier_display', read_only=True)
    
    class Meta:
        model = Shipment
        fields = [
            'id', 'carrier', 'carrier_display', 'tracking_number', 'tracking_url',
            'status', 'status_display', 'shipping_method', 'estimated_delivery',
            'shipped_at', 'delivered_at', 'items', 'shipping_cost'
        ]


class ShippingRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingRate
        fields = [
            'id', 'name', 'carrier', 'method', 'base_cost',
            'estimated_days_min', 'estimated_days_max', 'free_shipping_threshold'
        ]


class CalculateShippingSerializer(serializers.Serializer):
    postal_code = serializers.CharField(max_length=10)
    state = serializers.CharField(max_length=100, required=False)
    city = serializers.CharField(max_length=100, required=False)
    weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2, default=1)
    order_total = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)

