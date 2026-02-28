from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import InventoryLocation, Inventory, InventoryMovement
from .serializers import (
    InventoryLocationSerializer, InventorySerializer,
    InventoryMovementSerializer, StockUpdateSerializer
)
from .services import InventoryService


class InventoryLocationListView(generics.ListCreateAPIView):
    queryset = InventoryLocation.objects.filter(is_active=True)
    serializer_class = InventoryLocationSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class InventoryListView(generics.ListAPIView):
    """
    Listar inventario (con filtros)
    """
    serializer_class = InventorySerializer
    
    def get_queryset(self):
        queryset = Inventory.objects.select_related('variant', 'location')
        
        # Filtros
        location = self.request.query_params.get('location')
        variant = self.request.query_params.get('variant')
        low_stock = self.request.query_params.get('low_stock')
        
        if location:
            queryset = queryset.filter(location_id=location)
        if variant:
            queryset = queryset.filter(variant_id=variant)
        if low_stock:
            queryset = queryset.filter(quantity__lte=10)
        
        return queryset


class InventoryMovementListView(generics.ListAPIView):
    serializer_class = InventoryMovementSerializer
    
    def get_queryset(self):
        queryset = InventoryMovement.objects.select_related('variant', 'location')
        
        # Filtros
        variant = self.request.query_params.get('variant')
        location = self.request.query_params.get('location')
        reason = self.request.query_params.get('reason')
        
        if variant:
            queryset = queryset.filter(variant_id=variant)
        if location:
            queryset = queryset.filter(location_id=location)
        if reason:
            queryset = queryset.filter(reason=reason)
        
        return queryset.order_by('-created_at')[:100]  # Limitar a últimos 100


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_stock(request):
    """
    Actualizar stock manualmente (ajuste de inventario)
    """
    serializer = StockUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        inventory = Inventory.objects.get(
            variant_id=data['variant_id'],
            location_id=data['location_id']
        )
        inventory.adjust(data['new_quantity'], data.get('reason', 'Manual adjustment'))
        
        return Response({
            'message': 'Stock actualizado',
            'inventory': InventorySerializer(inventory).data
        })
    except Inventory.DoesNotExist:
        return Response(
            {'error': 'Inventario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def check_stock(request, variant_id):
    """
    Verificar disponibilidad de stock para una variante
    """
    summary = InventoryService.get_stock_summary(variant_id)
    return Response(summary)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reserve_items(request):
    """
    Reservar items (usado internamente por el carrito/ordenes)
    """
    items = request.data.get('items', [])
    reserved = []
    errors = []
    
    for item in items:
        try:
            inventory = InventoryService.reserve_stock(
                variant_id=item['variant_id'],
                location_id=item.get('location_id', 1),  # Default location
                quantity=item['quantity'],
                reference_id=item.get('reference_id')
            )
            reserved.append({
                'variant_id': item['variant_id'],
                'reserved': item['quantity'],
                'available_remaining': inventory.available_quantity
            })
        except Exception as e:
            errors.append({
                'variant_id': item['variant_id'],
                'error': str(e)
            })
    
    return Response({
        'success': len(errors) == 0,
        'reserved': reserved,
        'errors': errors
    })

