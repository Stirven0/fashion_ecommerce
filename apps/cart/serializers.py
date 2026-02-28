from rest_framework import serializers

from .models import Cart, CartItem
from apps.catalog.serializers import ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    product_slug = serializers.CharField(source='variant.product.slug', read_only=True)
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'variant', 'variant_details', 'product_name', 'product_slug',
            'quantity', 'unit_price', 'subtotal', 'main_image'
        ]
        read_only_fields = ['unit_price']
    
    def get_main_image(self, obj):
        from apps.catalog.serializers import ProductImageSerializer
        main_img = obj.variant.product.main_image
        if main_img:
            return ProductImageSerializer(main_img).data
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'subtotal', 'total', 'status', 'created_at']


class AddToCartSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(min_value=0, required=True)

