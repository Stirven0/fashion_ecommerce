import re
from decimal import Decimal, ROUND_HALF_UP


class MoneyHelper:
    """
    Helper para operaciones con dinero
    """
    
    @staticmethod
    def round(value):
        """Redondear a 2 decimales"""
        return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_percentage(amount, percentage):
        """Calcular porcentaje de un monto"""
        return MoneyHelper.round(amount * Decimal(str(percentage)) / 100)
    
    @staticmethod
    def apply_discount(amount, discount_type, discount_value):
        """Aplicar descuento a monto"""
        if discount_type == 'percentage':
            discount = MoneyHelper.calculate_percentage(amount, discount_value)
        elif discount_type == 'fixed_amount':
            discount = min(Decimal(str(discount_value)), amount)
        else:
            discount = Decimal('0')
        
        return MoneyHelper.round(amount - discount)


class ValidationHelper:
    """
    Helper para validaciones comunes
    """
    
    @staticmethod
    def validate_postal_code_mx(cp):
        """Validar código postal mexicano"""
        return re.match(r'^\d{5}$', str(cp)) is not None
    
    @staticmethod
    def validate_rfc(rfc):
        """Validar RFC mexicano básico"""
        pattern = r'^[A-ZÑ&]{3,4}\d{6}[A-Z\d]{3}$'
        return re.match(pattern, rfc.upper()) is not None
    
    @staticmethod
    def sanitize_phone(phone):
        """Limpiar número de teléfono"""
        return re.sub(r'\D', '', str(phone))


class CacheHelper:
    """
    Helper para operaciones de cache
    """
    
    @staticmethod
    def get_product_cache_key(product_id):
        return f"product:{product_id}"
    
    @staticmethod
    def get_category_tree_key():
        return "categories:tree"
    
    @staticmethod
    def invalidate_product_cache(product_id):
        from django.core.cache import cache
        cache.delete(f"product:{product_id}")

