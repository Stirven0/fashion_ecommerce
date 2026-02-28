from rest_framework import serializers

from .models import Coupon, CouponUsage, Promotion


class CouponSerializer(serializers.ModelSerializer):
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'code', 'description', 'discount_type', 'discount_type_display',
            'discount_value', 'min_purchase_amount', 'valid_until', 'is_valid'
        ]
    
    def get_is_valid(self, obj):
        valid, _ = obj.is_valid()
        return valid


class ValidateCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    cart_total = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)


class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    cart_id = serializers.IntegerField()


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = [
            'id', 'name', 'description', 'discount_type', 'discount_value',
            'min_purchase_amount', 'valid_until'
        ]

