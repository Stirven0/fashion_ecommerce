from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer, OrderDetailSerializer,
    CreateOrderSerializer, UpdateOrderStatusSerializer
)
from .services import OrderService


class OrderListView(generics.ListAPIView):
    """
    Listar órdenes del usuario autenticado
    """
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        
        # Filtro por estado
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related().prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    """
    Ver detalle de una orden
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        # Staff puede ver todas, usuarios solo las suyas
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_order(request):
    """
    Crear orden desde el carrito actual
    """
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Obtener carrito
    from apps.cart.services import CartService
    cart = CartService.get_or_create_cart(request)
    
    if not cart.items.exists():
        return Response(
            {'error': 'El carrito está vacío'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        order = OrderService.create_from_cart(
            user=request.user,
            cart=cart,
            shipping_address_id=data['shipping_address_id'],
            billing_address_id=data['billing_address_id'],
            notes=data.get('notes', '')
        )
        
        return Response({
            'message': 'Orden creada exitosamente',
            'order': OrderDetailSerializer(order).data
        }, status=status.HTTP_201_CREATED)
        
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, order_id):
    """
    Cancelar una orden (solo si está pendiente o confirmada)
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status not in ['pending', 'confirmed']:
        return Response(
            {'error': 'No se puede cancelar esta orden en su estado actual'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        order.cancel(reason=request.data.get('reason', 'Cancelado por cliente'))
        return Response({
            'message': 'Orden cancelada',
            'order': OrderListSerializer(order).data
        })
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Admin Views

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_order_list(request):
    """
    Listado completo de órdenes para admin
    """
    orders = Order.objects.all().select_related('user').prefetch_related('items')
    
    # Filtros
    status = request.query_params.get('status')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    user_id = request.query_params.get('user_id')
    
    if status:
        orders = orders.filter(status=status)
    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__lte=date_to)
    if user_id:
        orders = orders.filter(user_id=user_id)
    
    # Paginación simple
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = orders.count()
    orders_page = orders[start:end]
    
    return Response({
        'count': total,
        'results': OrderListSerializer(orders_page, many=True).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_order_status(request, order_id):
    """
    Actualizar estado de orden (Admin)
    """
    order = get_object_or_404(Order, id=order_id)
    serializer = UpdateOrderStatusSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        order.update_status(
            data['status'],
            user=request.user,
            notes=data.get('notes', '')
        )
        return Response({
            'message': 'Estado actualizado',
            'order': OrderDetailSerializer(order).data
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

