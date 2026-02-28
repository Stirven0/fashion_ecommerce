from django.db import models

from apps.core.models import TimeStampedModel
from apps.orders.models import Order, OrderItem


class Shipment(TimeStampedModel):
    """
    Envíos/Entregas de órdenes
    """
    STATUS_CHOICES = [
        ('preparing', 'En Preparación'),
        ('ready', 'Listo para Enviar'),
        ('shipped', 'En Tránsito'),
        ('in_transit', 'En Ruta'),
        ('out_for_delivery', 'En Reparto'),
        ('delivered', 'Entregado'),
        ('failed', 'Entrega Fallida'),
        ('returned', 'Devuelto'),
    ]
    
    CARRIER_CHOICES = [
        ('fedex', 'FedEx'),
        ('dhl', 'DHL'),
        ('ups', 'UPS'),
        ('redpack', 'Redpack'),
        ('estafeta', 'Estafeta'),
        ('local', 'Mensajería Local'),
        ('internal', 'Entrega Propia'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='shipments',
        db_column='order_id'
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='preparing')
    
    # Información del carrier
    carrier = models.CharField(max_length=50, choices=CARRIER_CHOICES)
    tracking_number = models.CharField(max_length=255, blank=True, db_index=True)
    tracking_url = models.URLField(blank=True)
    shipping_label_url = models.URLField(blank=True)
    
    # Dirección de envío (snapshot)
    shipping_address = models.JSONField(default=dict)
    
    # Costos
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_method = models.CharField(max_length=100, default='standard')
    
    # Fechas estimadas/reales
    estimated_delivery = models.DateField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Notas
    notes = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'shipments'
        ordering = ['-created_at']
        verbose_name = 'envío'
        verbose_name_plural = 'envíos'
    
    def __str__(self):
        return f"Shipment {self.id} - {self.carrier} - {self.status}"


class ShipmentItem(models.Model):
    """
    Items incluidos en un envío (una orden puede tener múltiples envíos)
    """
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='shipment_id'
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='shipment_items',
        db_column='order_item_id'
    )
    quantity = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'shipment_items'
        unique_together = ['shipment', 'order_item']
    
    def __str__(self):
        return f"{self.quantity}x {self.order_item.sku} in Shipment {self.shipment_id}"


class ShippingRate(models.Model):
    """
    Tarifas de envío por zona/peso
    """
    name = models.CharField(max_length=100)
    carrier = models.CharField(max_length=50, choices=Shipment.CARRIER_CHOICES)
    method = models.CharField(max_length=50)  # standard, express, overnight
    
    # Condiciones
    state = models.CharField(max_length=100, blank=True, help_text="Estado/Provincia")
    city = models.CharField(max_length=100, blank=True)
    postal_code_prefix = models.CharField(max_length=10, blank=True)
    
    # Precios
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    weight_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_shipping_threshold = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text="Monto mínimo para envío gratis"
    )
    
    estimated_days_min = models.PositiveIntegerField(default=3)
    estimated_days_max = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'shipping_rates'
        ordering = ['base_cost']
    
    def __str__(self):
        return f"{self.name} - {self.carrier} ({self.base_cost})"
    
    def calculate_cost(self, weight_kg=0, order_total=0):
        """Calcular costo de envío"""
        if self.free_shipping_threshold and order_total >= self.free_shipping_threshold:
            return 0
        
        return self.base_cost + (weight_kg * self.weight_per_kg)

