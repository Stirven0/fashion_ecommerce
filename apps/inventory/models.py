from django.db import models, transaction
from django.core.validators import MinValueValidator

from apps.core.models import TimeStampedModel
from apps.catalog.models import ProductVariant


class InventoryLocation(TimeStampedModel):
    """
    Ubicaciones de inventario (bodegas, tiendas físicas)
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'inventory_locations'
        verbose_name = 'ubicación de inventario'
        verbose_name_plural = 'ubicaciones de inventario'
    
    def __str__(self):
        return self.name


class Inventory(TimeStampedModel):
    """
    Stock por variante y ubicación
    """
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='inventories',
        db_column='variant_id'
    )
    location = models.ForeignKey(
        InventoryLocation,
        on_delete=models.CASCADE,
        related_name='inventories',
        db_column='location_id'
    )
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reserved = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'inventory'
        unique_together = ['variant', 'location']
        verbose_name = 'inventario'
        verbose_name_plural = 'inventarios'
    
    def __str__(self):
        return f"{self.variant.sku} @ {self.location.name}: {self.available_quantity}"
    
    @property
    def available_quantity(self):
        return max(0, self.quantity - self.reserved)
    
    def reserve(self, amount):
        """Reservar stock"""
        if amount > self.available_quantity:
            raise ValueError("Insufficient stock")
        self.reserved += amount
        self.save(update_fields=['reserved'])
    
    def release(self, amount):
        """Liberar reserva"""
        self.reserved = max(0, self.reserved - amount)
        self.save(update_fields=['reserved'])
    
    def adjust(self, new_quantity, reason="Manual adjustment"):
        """Ajustar inventario con tracking"""
        old_quantity = self.quantity
        difference = new_quantity - old_quantity
        
        with transaction.atomic():
            self.quantity = new_quantity
            self.save()
            
            # Registrar movimiento
            InventoryMovement.objects.create(
                variant=self.variant,
                location=self.location,
                change_qty=difference,
                reason=reason,
                reference_type='adjustment'
            )


class InventoryMovement(TimeStampedModel):
    """
    Movimientos de inventario (auditoría)
    """
    MOVEMENT_TYPES = [
        ('purchase', 'Compra/Entrada'),
        ('sale', 'Venta/Salida'),
        ('adjustment', 'Ajuste'),
        ('return', 'Devolución'),
        ('transfer', 'Transferencia'),
        ('reservation', 'Reserva'),
        ('release', 'Liberación'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='movements',
        db_column='variant_id'
    )
    location = models.ForeignKey(
        InventoryLocation,
        on_delete=models.CASCADE,
        related_name='movements',
        db_column='location_id'
    )
    change_qty = models.IntegerField(help_text="Positivo para entrada, negativo para salida")
    reason = models.CharField(max_length=100, choices=MOVEMENT_TYPES)
    reference_id = models.CharField(max_length=100, blank=True, help_text="ID de orden, factura, etc.")
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'inventory_movements'
        ordering = ['-created_at']
        verbose_name = 'movimiento de inventario'
        verbose_name_plural = 'movimientos de inventario'
    
    def __str__(self):
        direction = "↑" if self.change_qty > 0 else "↓"
        return f"{direction} {abs(self.change_qty)} {self.variant.sku} ({self.reason})"

