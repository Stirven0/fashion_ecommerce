from django.db import models, transaction
from django.contrib.auth import get_user_model

from apps.core.models import TimeStampedModel
from apps.catalog.models import ProductVariant

User = get_user_model()


class Order(TimeStampedModel):
    """
    Pedidos/Órdenes de compra
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('processing', 'En Proceso'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        db_column='user_id'
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Direcciones (snapshot en momento de orden)
    shipping_address = models.JSONField(default=dict)
    billing_address = models.JSONField(default=dict)
    
    # Metadatos
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Notas del cliente")
    internal_notes = models.TextField(blank=True, help_text="Notas internas del staff")
    
    # Timestamps específicos del flujo
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Order #{self.id} - {self.status}"
    
    def calculate_total(self):
        """Recalcular total basado en items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total
    
    def update_status(self, new_status, user=None, notes=""):
        """Actualizar estado con historial"""
        old_status = self.status
        self.status = new_status
        
        # Actualizar timestamps específicos
        from django.utils import timezone
        if new_status == 'confirmed':
            self.confirmed_at = timezone.now()
        elif new_status == 'shipped':
            self.shipped_at = timezone.now()
        elif new_status == 'delivered':
            self.delivered_at = timezone.now()
        
        self.save()
        
        # Crear historial
        OrderStatusHistory.objects.create(
            order=self,
            status=new_status,
            previous_status=old_status,
            changed_by=user,
            notes=notes
        )
    
    def cancel(self, reason="", user=None):
        """Cancelar orden y liberar stock"""
        if self.status in ['delivered', 'refunded']:
            raise ValueError("No se puede cancelar una orden entregada o reembolsada")
        
        # Liberar reservas de inventario
        for item in self.items.all():
            from apps.inventory.models import Inventory
            inventories = Inventory.objects.filter(variant=item.variant)
            for inv in inventories:
                if inv.reserved >= item.quantity:
                    inv.release(item.quantity)
                    break
        
        self.update_status('cancelled', user, f"Cancelado: {reason}")
    
    @property
    def is_paid(self):
        return self.payments.filter(status='completed').exists()


class OrderStatusHistory(TimeStampedModel):
    """
    Historial de cambios de estado
    """
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        db_column='order_id'
    )
    status = models.CharField(max_length=50)
    previous_status = models.CharField(max_length=50, blank=True)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'order_status_history'
        ordering = ['-created_at']
        verbose_name = 'historial de estado'
        verbose_name_plural = 'historial de estados'
    
    def __str__(self):
        return f"Order {self.order_id}: {self.previous_status} → {self.status}"


class OrderItem(models.Model):
    """
    Items de una orden (snapshot del producto en momento de compra)
    """
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='order_id'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        db_column='variant_id'
    )
    
    # Snapshot de datos
    sku = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    variant_description = models.CharField(max_length=255, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Para devoluciones
    returned_quantity = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'item de orden'
        verbose_name_plural = 'items de orden'
    
    def __str__(self):
        return f"{self.quantity}x {self.sku}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    @property
    def available_for_return(self):
        return self.quantity - self.returned_quantity

