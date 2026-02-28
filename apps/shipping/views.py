from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Shipment, ShippingRate
from .serializers import (
    ShipmentSerializer, ShippingRateSerializer, CalculateShippingSerializer
)
from .services import ShippingService


@api_view(['POST'])
def calculate_shipping(request):
    """
    Calcular opciones de envío para un código postal
    """
    serializer = CalculateShippingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    rates = ShippingService.calculate_rates(
        postal_code=data['postal_code'],
        state=data.get('state', ''),
        city=data.get('city', ''),
        weight_kg=float(data.get('weight_kg', 1)),
        order_total=float(data.get('order_total', 0))
    )
    
    return Response({
        'postal_code': data['postal_code'],
        'options': rates
    })


class ShipmentListView(generics.ListAPIView):
    """
    Listar envíos (admin) o envíos de mis órdenes (cliente)
    """
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Shipment.objects.all()
        return Shipment.objects.filter(order__user=self.request.user)


class ShipmentDetailView(generics.RetrieveAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Shipment.objects.all()
        return Shipment.objects.filter(order__user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_shipment(request):
    """
    Crear envío para una orden (Admin)
    """
    order_id = request.data.get('order_id')
    carrier = request.data.get('carrier')
    items = request.data.get('items', [])  # [{order_item_id, quantity}]
    
    from apps.orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Orden no encontrada'}, status=404)
    
    shipment = ShippingService.create_shipment(order, carrier, 'standard')
    
    # Generar tracking si no se proporciona
    if not shipment.tracking_number:
        shipment.tracking_number = ShippingService.generate_tracking(carrier)
        shipment.save()
    
    return Response({
        'shipment': ShipmentSerializer(shipment).data,
        'message': 'Envío creado exitosamente'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_shipment_tracking(request, shipment_id):
    """
    Actualizar tracking de envío
    """
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return Response({'error': 'Envío no encontrado'}, status=404)
    
    tracking_number = request.data.get('tracking_number')
    status = request.data.get('status', 'shipped')
    
    ShippingService.update_tracking(shipment, tracking_number, status)
    
    return Response({
        'message': 'Tracking actualizado',
        'shipment': ShipmentSerializer(shipment).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def track_shipment(request, tracking_number):
    """
    Rastrear envío por número de guía
    """
    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
        
        # Verificar permisos
        if not request.user.is_staff and shipment.order.user != request.user:
            return Response({'error': 'No autorizado'}, status=403)
        
        # Aquí se integraría con API del carrier
        # Por ahora retornamos datos locales
        return Response({
            'tracking_number': tracking_number,
            'carrier': shipment.carrier,
            'status': shipment.status,
            'estimated_delivery': shipment.estimated_delivery,
            'history': [
                {'status': 'shipped', 'date': shipment.shipped_at, 'location': 'Centro de distribución'},
                {'status': 'in_transit', 'date': shipment.updated_at, 'location': 'En ruta'},
            ]
        })
        
    except Shipment.DoesNotExist:
        return Response({'error': 'Número de guía no encontrado'}, status=404)

