from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Payment, PaymentMethod
from .serializers import PaymentSerializer, CreatePaymentSerializer, PaymentMethodSerializer
from .services import PaymentService


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment(request):
    """
    Iniciar proceso de pago para una orden
    """
    serializer = CreatePaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Verificar que la orden pertenece al usuario
    from apps.orders.models import Order
    try:
        order = Order.objects.get(
            id=data['order_id'],
            user=request.user,
            status='pending'
        )
    except Order.DoesNotExist:
        return Response(
            {'error': 'Orden no encontrada o no disponible para pago'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        result = PaymentService.create_payment(
            order=order,
            method=data['method'],
            token=data.get('token'),
            saved_method_id=data.get('use_saved_method')
        )
        return Response(result)
        
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_detail(request, payment_id):
    """
    Ver detalle de un pago
    """
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        order__user=request.user
    )
    return Response(PaymentSerializer(payment).data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Webhooks no requieren auth
def stripe_webhook(request):
    """
    Webhook para eventos de Stripe
    """
    payload = request.data
    
    # Verificar firma en producción
    # sig_header = request.headers.get('Stripe-Signature')
    
    success = PaymentService.process_webhook('stripe', payload)
    
    if success:
        return Response({'status': 'processed'})
    return Response({'status': 'ignored'}, status=200)


# Métodos de pago guardados

class PaymentMethodListView(generics.ListAPIView):
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(
            user=self.request.user,
            is_active=True
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def setup_payment_method(request):
    """
    Configurar nuevo método de pago (Stripe SetupIntent)
    """
    import stripe
    from django.conf import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Crear SetupIntent para guardar método de pago
        setup_intent = stripe.SetupIntent.create(
            customer=request.user.profile.stripe_customer_id if hasattr(request.user.profile, 'stripe_customer_id') else None,
            payment_method_types=['card'],
            metadata={'user_id': request.user.id}
        )
        
        return Response({
            'client_secret': setup_intent.client_secret
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

