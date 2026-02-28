from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import TimeStampedModel
from apps.catalog.models import Category, Product, Brand


class Coupon(TimeStampedModel):
    """
    Cupones de descuento
    """
    DISCOUNT_TYPES = [
        ('percentage', 'Porcentaje'),
        ('fixed_amount', 'Monto Fijo'),
        ('free_shipping', 'Envío Gratis'),
    ]
    
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Porcentaje (0-100) o monto fijo"
    )
    
    # Límites de uso
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)
    
    # Restricciones
    min_purchase_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Aplicabilidad
    applicable_products = models.ManyToManyField(Product, blank=True)
    applicable_categories = models.ManyToManyField(Category, blank=True)
    applicable_brands = models.ManyToManyField(Brand, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'coupons'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"
    
    def is_valid(self, user=None, cart_total=0):
        """Verificar si el cupón es válido para uso"""
        from django.utils import timezone
        
        now = timezone.now()
        
        if not self.is_active:
            return False, "Cupón inactivo"
        
        if now < self.valid_from:
            return False, "Cupón aún no válido"
        
        if self.valid_until and now > self.valid_until:
            return False, "Cupón expirado"
        
        if self.max_uses and self.current_uses >= self.max_uses:
            return False, "Límite de usos alcanzado"
        
        if self.min_purchase_amount and cart_total < self.min_purchase_amount:
            return False, f"Mínimo de compra: ${self.min_purchase_amount}"
        
        if user:
            # Verificar usos por usuario
            user_uses = CouponUsage.objects.filter(coupon=self, user=user).count()
            if user_uses >= self.max_uses_per_user:
                return False, "Ya usaste este cupón"
        
        return True, "Válido"
    
    def calculate_discount(self, subtotal, items=None):
        """Calcular monto de descuento"""
        if self.discount_type == 'percentage':
            return (subtotal * self.discount_value) / 100
        elif self.discount_type == 'fixed_amount':
            return min(self.discount_value, subtotal)
        elif self.discount_type == 'free_shipping':
            # El descuento se aplica al envío, no al subtotal
            return 0
        
        return 0


class CouponUsage(TimeStampedModel):
    """
    Registro de uso de cupones
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'coupon_usages'
        unique_together = ['coupon', 'order']
    
    def __str__(self):
        return f"{self.coupon.code} used by {self.user} on Order {self.order_id}"


class Promotion(TimeStampedModel):
    """
    Promociones automáticas (sin código)
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=20, choices=Coupon.DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Condiciones
    min_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    buy_x_get_y = models.JSONField(default=dict, blank=True, help_text="{'buy': 2, 'get': 1, 'discount': 50}")
    
    # Aplicabilidad
    applicable_products = models.ManyToManyField(Product, blank=True)
    applicable_categories = models.ManyToManyField(Category, blank=True)
    
    priority = models.PositiveIntegerField(default=0, help_text="Mayor número = mayor prioridad")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'promotions'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.name

