from django.db import models, transaction
from django.contrib.auth import get_user_model

from apps.core.models import TimeStampedModel
from apps.catalog.models import ProductVariant

User = get_user_model()


class Cart(TimeStampedModel):
    """
    Carrito de compras
    """
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('converted', 'Convertido a Orden'),
        ('abandoned', 'Abandonado'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart',
        db_column='user_id'
    )
    session_id = models.CharField(max_length=255, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'carrito'
        verbose_name_plural = 'carritos'
    
    def __str__(self):
        return f"Cart {self.id} - {self.user or self.session_id}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def total(self):
        # Aquí se aplicarían descuentos, impuestos, envío
        return self.subtotal
    
    def add_item(self, variant, quantity=1):
        """Agregar item al carrito"""
        if quantity <= 0:
            raise ValueError("Cantidad debe ser positiva")
        
        with transaction.atomic():
            item, created = CartItem.objects.get_or_create(
                cart=self,
                variant=variant,
                defaults={'quantity': 0, 'unit_price': variant.price}
            )
            
            # Actualizar precio unitario (puede haber cambiado)
            item.unit_price = variant.price
            
            if not created:
                item.quantity += quantity
            else:
                item.quantity = quantity
            
            item.save()
            
            # Actualizar timestamps
            self.save()
            
            return item
    
    def update_item(self, variant_id, quantity):
        """Actualizar cantidad de un item"""
        try:
            item = self.items.get(variant_id=variant_id)
            if quantity <= 0:
                item.delete()
                return None
            item.quantity = quantity
            item.save()
            return item
        except CartItem.DoesNotExist:
            return None
    
    def remove_item(self, variant_id):
        """Remover item del carrito"""
        self.items.filter(variant_id=variant_id).delete()
    
    def clear(self):
        """Vaciar carrito"""
        self.items.all().delete()
    
    def merge_with(self, other_cart):
        """
        Fusionar otro carrito en este (útil cuando usuario inicia sesión)
        """
        for item in other_cart.items.all():
            self.add_item(item.variant, item.quantity)
        other_cart.delete()


class CartItem(models.Model):
    """
    Items del carrito
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='cart_id'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='cart_items',
        db_column='variant_id'
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'variant']
        verbose_name = 'item de carrito'
        verbose_name_plural = 'items de carrito'
    
    def __str__(self):
        return f"{self.quantity}x {self.variant.sku}"
    
    @property
    def subtotal(self):
        return self.unit_price * self.quantity
    
    def validate_stock(self):
        """Validar que hay stock suficiente"""
        available = self.variant.total_stock
        if self.quantity > available:
            raise ValueError(
                f"Stock insuficiente para {self.variant}. "
                f"Disponible: {available}, Solicitado: {self.quantity}"
            )

