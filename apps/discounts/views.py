from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Coupon, Promotion
from .serializers import (
    CouponSerializer, ValidateCouponSerializer,
    ApplyCouponSerializer, PromotionSerializer
)
from .services import DiscountService


@api_view(['POST'])
def validate_coupon(request):
    """
    Validar un cupón sin aplicarlo
    """
    serializer = ValidateCouponSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    user = request.user if request.user.is_authenticated else None
    
    result, message = DiscountService.validate_coupon(
        code=data['code'],
        user=user,
        cart_total=data['cart_total']
    )
    
    if result is None:
        return Response({'valid': False, 'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'valid': True,
        'coupon': {
            'code': result['code'],
            'type': result['discount_type'],
            'value': result['discount_value'],
            'discount_amount': result['discount_amount'],
            'new_total': result['new_total']
        }
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_coupon_to_order(request):
    """
    Aplicar cupón a una orden existente (antes de pago)
    """
    serializer = ApplyCouponSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Verificar orden
    from apps.orders.models import Order
    try:
        order = Order.objects.get(
            id=data['cart_id'],
            user=request.user,
            status='pending'
        )
    except Order.DoesNotExist:
        return Response({'error': 'Orden no encontrada'}, status=404)
    
    # Validar cupón
    result, message = DiscountService.validate_coupon(
        code=data['code'],
        user=request.user,
        cart_total=order.total_amount
    )
    
    if result is None:
        return Response({'error': message}, status=400)
    
    # Verificar que no se haya aplicado ya
    if hasattr(order, 'coupon_usages') and order.coupon_usages.exists():
        return Response({'error': 'Ya se aplicó un cupón a esta orden'}, status=400)
    
    # Aplicar
    discount = DiscountService.apply_coupon(result['coupon'], order, request.user)
    
    return Response({
        'message': 'Cupón aplicado exitosamente',
        'discount_amount': float(discount),
        'new_total': float(order.total_amount)
    })


class PromotionListView(generics.ListAPIView):
    """
    Listar promociones activas
    """
    serializer_class = PromotionSerializer
    
    def get_queryset(self):
        from django.utils import timezone
        now = timezone.now()
        return Promotion.objects.filter(
            is_active=True,
            valid_from__lte=now
        ).filter(
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now)
        )


# Admin views para gestión de cupones
class CouponAdminView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        # Convertir código a mayúsculas
        code = self.request.data.get('code', '').upper()
        serializer.save(code=code)

