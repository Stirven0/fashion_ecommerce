from django.db import models
from django.contrib.auth import get_user_model

from apps.core.models import TimeStampedModel
from apps.orders.models import Order

User = get_user_model()


class Payment(TimeStampedModel):
    """
    Registro de pagos
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
        ('cancelled', 'Cancelado'),
    ]
    
    METHOD_CHOICES = [
        ('credit_card', 'Tarjeta de Crédito'),
        ('debit_card', 'Tarjeta de Débito'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('mercadopago', 'Mercado Pago'),
        ('oxxo', 'OXXO'),
        ('spei', 'SPEI/Transferencia'),
        ('cash_on_delivery', 'Contra Entrega'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        db_column='order_id'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    
    # Datos del procesador de pagos
    provider = models.CharField(max_length=50, blank=True, help_text="Stripe, PayPal, etc.")
    provider_payment_id = models.CharField(max_length=255, blank=True, db_index=True)
    provider_response = models.JSONField(default=dict, blank=True)
    
    # Metadatos de tarjeta (enmascarados)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)
    
    # Intentos de pago
    attempt_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    # Timestamps específicos
    paid_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        verbose_name = 'pago'
        verbose_name_plural = 'pagos'
    
    def __str__(self):
        return f"Payment {self.id} - {self.order_id} - {self.status}"
    
    def mark_as_completed(self, provider_response=None):
        """Marcar pago como completado"""
        from django.utils import timezone
        self.status = 'completed'
        self.paid_at = timezone.now()
        if provider_response:
            self.provider_response = provider_response
        self.save()
        
        # Actualizar orden
        from apps.orders.services import OrderService
        OrderService.confirm_order(self.order)
    
    def mark_as_failed(self, error_message):
        """Marcar pago como fallido"""
        self.status = 'failed'
        self.error_message = error_message
        self.attempt_count += 1
        self.save()


class PaymentMethod(models.Model):
    """
    Métodos de pago guardados por el usuario (para futuros usos)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_payment_methods'
    )
    provider = models.CharField(max_length=50)  # stripe, paypal, etc.
    provider_customer_id = models.CharField(max_length=255)
    provider_payment_method_id = models.CharField(max_length=255)
    
    # Info enmascarada para display
    type = models.CharField(max_length=50)  # card, bank_transfer, etc.
    last_four = models.CharField(max_length=4)
    brand = models.CharField(max_length=50, blank=True)
    expiry_month = models.CharField(max_length=2, blank=True)
    expiry_year = models.CharField(max_length=4, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_payment_methods'
    
    def __str__(self):
        return f"{self.brand} ****{self.last_four}"
