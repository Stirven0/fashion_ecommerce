from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Order, OrderItem
from apps.cart.models import Cart
from apps.cart.services import CartService
from apps.inventory.services import InventoryService


class OrderService:
    """
    Servicio para creación y gestión de órdenes
    """
    
    @staticmethod
    @transaction.atomic
    def create_from_cart(user, cart, shipping_address_id, billing_address_id, notes=""):
        """
        Crear orden desde un carrito
        """
        from apps.accounts.models import Address
        
        # Validar carrito
        CartService.validate_cart_for_checkout(cart)
        
        # Obtener direcciones
        try:
            shipping_addr = Address.objects.get(id=shipping_address_id, user=user)
            billing_addr = Address.objects.get(id=billing_address_id, user=user)
        except Address.DoesNotExist:
            raise ValidationError("Dirección no encontrada")
        
        # Crear orden
        order = Order.objects.create(
            user=user,
            status='pending',
            shipping_address=shipping_addr.to_dict(),
            billing_address=billing_addr.to_dict(),
            notes=notes,
            ip_address=None,  # Se puede obtener del request
        )
        
        # Crear items de la orden
        order_items = []
        for cart_item in cart.items.select_related('variant', 'variant__product'):
            order_items.append(OrderItem(
                order=order,
                variant=cart_item.variant,
                sku=cart_item.variant.sku,
                product_name=cart_item.variant.product.name,
                variant_description=f"{cart_item.variant.size} / {cart_item.variant.color}",
                unit_price=cart_item.unit_price,
                quantity=cart_item.quantity
            ))
        
        OrderItem.objects.bulk_create(order_items)
        
        # Calcular total
        order.calculate_total()
        
        # Reservar inventario
        try:
            CartService.reserve_cart_items(cart, order_reference=str(order.id))
        except ValidationError as e:
            # Si falla la reserva, cancelar orden
            order.delete()
            raise ValidationError(f"No se pudo reservar inventario: {e.detail}")
        
        # Convertir carrito
        cart.status = 'converted'
        cart.save()
        
        # Crear historial inicial
        from .models import OrderStatusHistory
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Orden creada desde carrito'
        )
        
        return order
    
    @staticmethod
    @transaction.atomic
    def confirm_order(order, user=None):
        """
        Confirmar orden (después de pago exitoso)
        """
        if order.status != 'pending':
            raise ValidationError("Solo órdenes pendientes pueden ser confirmadas")
        
        # Confirmar venta en inventario (mover de reservado a vendido)
        for item in order.items.all():
            from apps.inventory.models import Inventory
            inventories = Inventory.objects.filter(variant=item.variant, reserved__gt=0)
            
            remaining = item.quantity
            for inv in inventories:
                if remaining <= 0:
                    break
                    
                to_confirm = min(inv.reserved, remaining)
                try:
                    InventoryService.confirm_sale(
                        variant_id=item.variant_id,
                        location_id=inv.location_id,
                        quantity=to_confirm,
                        reference_id=str(order.id)
                    )
                    remaining -= to_confirm
                except Exception:
                    # Log error pero continuar
                    pass
        
        order.update_status('confirmed', user, 'Pago confirmado')
        return order
    
    @staticmethod
    def get_user_orders(user, status=None):
        """
        Obtener órdenes de un usuario con filtros opcionales
        """
        orders = Order.objects.filter(user=user).prefetch_related('items', 'status_history')
        if status:
            orders = orders.filter(status=status)
        return orders.order_by('-created_at')

