from rest_framework import serializers

from .models import Payment, PaymentMethod


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'method', 'method_display', 'status', 'status_display',
            'provider', 'card_last_four', 'card_brand', 'paid_at', 'created_at'
        ]


class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)
    # Campos específicos por método
    token = serializers.CharField(required=False, help_text="Token del procesador de pagos")
    use_saved_method = serializers.IntegerField(required=False, help_text="ID de método guardado")


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'type', 'last_four', 'brand',
            'expiry_month', 'expiry_year', 'is_default'
        ]

