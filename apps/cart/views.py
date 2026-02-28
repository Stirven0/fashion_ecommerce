from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer
from .services import CartService


class CartDetailView(generics.RetrieveAPIView):
    """
    Ver carrito actual
    """
    serializer_class = CartSerializer
    
    def get_object(self):
        cart = CartService.get_or_create_cart(self.request)
        return cart


@api_view(['POST'])
def add_to_cart(request):
    """
    Agregar producto al carrito
    """
    serializer = AddToCartSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    cart = CartService.get_or_create_cart(request)
    data = serializer.validated_data
    
    try:
        from apps.catalog.models import ProductVariant
        variant = ProductVariant.objects.get(
            id=data['variant_id'],
            active=True,
            product__active=True
        )
        
        # Verificar stock básico
        if variant.total_stock < data['quantity']:
            return Response({
                'error': 'Stock insuficiente',
                'available': variant.total_stock,
                'requested': data['quantity']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        item = cart.add_item(variant, data['quantity'])
        
        return Response({
            'message': 'Producto agregado al carrito',
            'cart': CartSerializer(cart).data,
            'item': {
                'variant_id': item.variant_id,
                'quantity': item.quantity,
                'subtotal': item.subtotal
            }
        })
        
    except ProductVariant.DoesNotExist:
        return Response(
            {'error': 'Variante de producto no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
def update_cart_item(request):
    """
    Actualizar cantidad de un item
    """
    serializer = UpdateCartItemSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    cart = CartService.get_or_create_cart(request)
    data = serializer.validated_data
    
    item = cart.update_item(data['variant_id'], data['quantity'])
    
    if item is None and data['quantity'] > 0:
        return Response(
            {'error': 'Item no encontrado en el carrito'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        'message': 'Carrito actualizado',
        'cart': CartSerializer(cart).data
    })


@api_view(['DELETE'])
def remove_from_cart(request, variant_id):
    """
    Eliminar item del carrito
    """
    cart = CartService.get_or_create_cart(request)
    cart.remove_item(variant_id)
    
    return Response({
        'message': 'Item eliminado',
        'cart': CartSerializer(cart).data
    })


@api_view(['POST'])
def clear_cart(request):
    """
    Vaciar carrito
    """
    cart = CartService.get_or_create_cart(request)
    cart.clear()
    
    return Response({
        'message': 'Carrito vaciado',
        'cart': CartSerializer(cart).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def merge_cart_on_login(request):
    """
    Endpoint para fusionar carrito de sesión al iniciar sesión
    (llamar desde frontend después de login)
    """
    cart = CartService.get_or_create_cart(request)
    return Response({
        'message': 'Carrito sincronizado',
        'cart': CartSerializer(cart).data
    })


@api_view(['GET'])
def validate_cart(request):
    """
    Validar carrito antes de checkout
    """
    cart = CartService.get_or_create_cart(request)
    
    try:
        CartService.validate_cart_for_checkout(cart)
        return Response({
            'valid': True,
            'message': 'Carrito listo para checkout',
            'cart': CartSerializer(cart).data
        })
    except ValidationError as e:
        return Response({
            'valid': False,
            'errors': e.detail
        }, status=status.HTTP_400_BAD_REQUEST)

