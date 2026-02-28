from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Inventory, InventoryMovement


class InventoryService:
    """
    Servicio para manejar operaciones complejas de inventario
    """
    
    @staticmethod
    @transaction.atomic
    def reserve_stock(variant_id, location_id, quantity, reference_id=None):
        """
        Reservar stock para un pedido
        """
        try:
            inventory = Inventory.objects.select_for_update().get(
                variant_id=variant_id,
                location_id=location_id
            )
        except Inventory.DoesNotExist:
            raise ValidationError("Producto no disponible en esta ubicación")
        
        if inventory.available_quantity < quantity:
            raise ValidationError(
                f"Stock insuficiente. Disponible: {inventory.available_quantity}, "
                f"Solicitado: {quantity}"
            )
        
        # Actualizar reserva
        inventory.reserve(quantity)
        
        # Registrar movimiento
        InventoryMovement.objects.create(
            variant_id=variant_id,
            location_id=location_id,
            change_qty=0,  # La cantidad física no cambia, solo la reserva
            reason='reservation',
            reference_id=reference_id or '',
            notes=f'Reservado: {quantity}'
        )
        
        return inventory
    
    @staticmethod
    @transaction.atomic
    def confirm_sale(variant_id, location_id, quantity, reference_id=None):
        """
        Confirmar venta (descontar de cantidad física y reserva)
        """
        inventory = Inventory.objects.select_for_update().get(
            variant_id=variant_id,
            location_id=location_id
        )
        
        # Verificar que tenemos suficiente reserva o stock
        if inventory.reserved >= quantity:
            inventory.reserved -= quantity
        else:
            # Si no hay reserva suficiente, verificar stock disponible
            if inventory.available_quantity < quantity:
                raise ValidationError("Stock insuficiente")
        
        inventory.quantity -= quantity
        inventory.save()
        
        # Registrar movimiento
        InventoryMovement.objects.create(
            variant_id=variant_id,
            location_id=location_id,
            change_qty=-quantity,
            reason='sale',
            reference_id=reference_id or ''
        )
        
        return inventory
    
    @staticmethod
    @transaction.atomic
    def restock(variant_id, location_id, quantity, reference_id=None, reason='purchase'):
        """
        Reabastecer inventario
        """
        inventory, created = Inventory.objects.get_or_create(
            variant_id=variant_id,
            location_id=location_id,
            defaults={'quantity': 0, 'reserved': 0}
        )
        
        inventory.quantity += quantity
        inventory.save()
        
        # Registrar movimiento
        InventoryMovement.objects.create(
            variant_id=variant_id,
            location_id=location_id,
            change_qty=quantity,
            reason=reason,
            reference_id=reference_id or ''
        )
        
        return inventory
    
    @staticmethod
    def get_stock_summary(variant_id):
        """
        Obtener resumen de stock de una variante en todas las ubicaciones
        """
        inventories = Inventory.objects.filter(variant_id=variant_id)
        
        total_quantity = sum(inv.quantity for inv in inventories)
        total_reserved = sum(inv.reserved for inv in inventories)
        
        return {
            'variant_id': variant_id,
            'total_quantity': total_quantity,
            'total_reserved': total_reserved,
            'available': total_quantity - total_reserved,
            'locations': [
                {
                    'location_id': inv.location_id,
                    'location_name': inv.location.name,
                    'quantity': inv.quantity,
                    'reserved': inv.reserved,
                    'available': inv.available_quantity
                }
                for inv in inventories
            ]
        }

