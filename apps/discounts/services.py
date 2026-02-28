from django.utils import timezone

from .models import Coupon, CouponUsage, Promotion


class DiscountService:
    """
    Servicio para aplicar descuentos y calcular totales
    """
    
    @staticmethod
    def validate_coupon(code, user=None, cart_total=0):
        """
        Validar un cupón y retornar información
        """
        try:
            coupon = Coupon.objects.get(code=code.upper(), is_active=True)
        except Coupon.DoesNotExist:
            return None, "Cupón no encontrado"
        
        is_valid, message = coupon.is_valid(user, cart_total)
        
        if not is_valid:
            return None, message
        
        discount_amount = coupon.calculate_discount(cart_total)
        
        return {
            'coupon': coupon,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value),
            'discount_amount': float(discount_amount),
            'new_total': float(cart_total - discount_amount)
        }, "Válido"
    
    @staticmethod
    def apply_coupon(coupon, order, user):
        """
        Aplicar cupón a una orden (después de creada)
        """
        discount_amount = coupon.calculate_discount(order.total_amount)
        
        # Actualizar total de orden
        order.total_amount -= discount_amount
        order.save()
        
        # Registrar uso
        CouponUsage.objects.create(
            coupon=coupon,
            user=user,
            order=order,
            discount_amount=discount_amount
        )
        
        # Incrementar contador
        coupon.current_uses += 1
        coupon.save()
        
        return discount_amount
    
    @staticmethod
    def get_active_promotions():
        """
        Obtener promociones activas actuales
        """
        now = timezone.now()
        return Promotion.objects.filter(
            is_active=True,
            valid_from__lte=now
        ).filter(
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=now)
        ).order_by('-priority')
    
    @staticmethod
    def calculate_best_discount(cart_items, subtotal):
        """
        Calcular el mejor descuento automático aplicable
        """
        promotions = DiscountService.get_active_promotions()
        best_discount = 0
        best_promotion = None
        
        for promo in promotions:
            # Verificar aplicabilidad
            if promo.min_purchase_amount and subtotal < promo.min_purchase_amount:
                continue
            
            # Calcular descuento
            discount = 0
            
            if promo.discount_type == 'percentage':
                discount = (subtotal * promo.discount_value) / 100
            elif promo.discount_type == 'fixed_amount':
                discount = min(promo.discount_value, subtotal)
            elif promo.buy_x_get_y:
                # Lógica de compra X lleva Y
                pass
            
            if discount > best_discount:
                best_discount = discount
                best_promotion = promo
        
        return {
            'promotion': best_promotion,
            'discount_amount': best_discount,
            'final_total': subtotal - best_discount
        }

