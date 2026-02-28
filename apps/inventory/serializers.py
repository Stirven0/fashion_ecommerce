from rest_framework import serializers

from .models import InventoryLocation, Inventory, InventoryMovement


class InventoryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLocation
        fields = ['id', 'name', 'address', 'is_active']


class InventorySerializer(serializers.ModelSerializer):
    variant_sku = serializers.CharField(source='variant.sku', read_only=True)
    variant_name = serializers.CharField(source='variant.product.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    available = serializers.IntegerField(source='available_quantity', read_only=True)
    
    class Meta:
        model = Inventory
        fields = [
            'variant', 'variant_sku', 'variant_name',
            'location', 'location_name',
            'quantity', 'reserved', 'available'
        ]


class InventoryMovementSerializer(serializers.ModelSerializer):
    variant_sku = serializers.CharField(source='variant.sku', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = [
            'id', 'variant', 'variant_sku', 'location', 'location_name',
            'change_qty', 'reason', 'reference_id', 'notes', 'created_at'
        ]


class StockUpdateSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    location_id = serializers.IntegerField()
    new_quantity = serializers.IntegerField(min_value=0)
    reason = serializers.CharField(required=False, allow_blank=True)

