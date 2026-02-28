from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Cart, CartItem
from apps.inventory.services import InventoryService


class CartService:
    """
    Servicio para operaciones complejas del carrito
    """
    
    @staticmethod
    def get_or_create_cart(request):
        """
        Obtener carrito existente o crear nuevo
        Soporta usuarios autenticados y sesiones anónimas
        """
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key
        
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        if user:
            # Buscar carrito del usuario
            cart, created = Cart.objects.get_or_create(
                user=user,
                defaults={'status': 'active'}
            )
            
            # Si hay carrito de sesión, fusionarlo
            if not created:
                session_cart = Cart.objects.filter(
                    session_id=session_id,
                    status='active'
                ).exclude(user=user).first()
                
                if session_cart:
                    cart.merge_with(session_cart)
            
            # Limpiar session_id si existe
            if cart.session_id:
                cart.session_id = ''
                cart.save()
                
        else:
            # Carrito anónimo por sesión
            cart, created = Cart.objects.get_or_create(
                session_id=session_id,
                user__isnull=True,
                status='active',
                defaults={'status': 'active'}
            )
        
        return cart
    
    @staticmethod
    def validate_cart_for_checkout(cart):
        """
        Validar que el carrito está listo para checkout
        """
        if not cart.items.exists():
            raise ValidationError("El carrito está vacío")
        
        errors = []
        for item in cart.items.select_related('variant'):
            try:
                item.validate_stock()
            except ValueError as e:
                errors.append({
                    'variant_id': item.variant_id,
                    'error': str(e)
                })
        
        if errors:
            raise ValidationError({
                'message': 'Algunos items no tienen stock suficiente',
                'errors': errors
            })
        
        return True
    
    @staticmethod
    def reserve_cart_items(cart, order_reference=None):
        """
        Reservar inventario para todos los items del carrito
        """
        reserved = []
        errors = []
        
        with transaction.atomic():
            for item in cart.items.all():
                try:
                    # Usar primera ubicación disponible por defecto
                    # En producción, esto debería ser más sofisticado
                    from apps.inventory.models import Inventory
                    inv = Inventory.objects.filter(
                        variant=item.variant,
                        available_quantity__gte=item.quantity
                    ).first()
                    
                    if not inv:
                        raise ValueError("No hay stock disponible en ninguna ubicación")
                    
                    InventoryService.reserve_stock(
                        variant_id=item.variant_id,
                        location_id=inv.location_id,
                        quantity=item.quantity,
                        reference_id=order_reference
                    )
                    reserved.append(item.variant_id)
                    
                except Exception as e:
                    errors.append({
                        'variant_id': item.variant_id,
                        'error': str(e)
                    })
            
            if errors:
                # Rollback implícito por transaction.atomic
                raise ValidationError({
                    'message': 'No se pudo reservar stock para todos los items',
                    'errors': errors
                })
        
        return reserved

