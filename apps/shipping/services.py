from django.db.models import Q

from .models import ShippingRate, Shipment


class ShippingService:
    """
    Servicio de cálculo y gestión de envíos
    """
    
    @staticmethod
    def calculate_rates(postal_code, state="", city="", weight_kg=1, order_total=0):
        """
        Calcular tarifas disponibles para una dirección
        """
        # Buscar tarifas aplicables
        query = Q(is_active=True)
        
        # Matching geográfico (más específico primero)
        if postal_code:
            query &= (Q(postal_code_prefix=postal_code[:3]) | Q(postal_code_prefix=''))
        if state:
            query &= (Q(state=state) | Q(state=''))
        if city:
            query &= (Q(city=city) | Q(city=''))
        
        rates = ShippingRate.objects.filter(query).order_by('base_cost')
        
        results = []
        for rate in rates:
            cost = rate.calculate_cost(weight_kg, order_total)
            results.append({
                'id': rate.id,
                'name': rate.name,
                'carrier': rate.carrier,
                'method': rate.method,
                'cost': float(cost),
                'estimated_days': {
                    'min': rate.estimated_days_min,
                    'max': rate.estimated_days_max
                },
                'free_shipping_available': (
                    rate.free_shipping_threshold and 
                    order_total >= rate.free_shipping_threshold
                )
            })
        
        return results
    
    @staticmethod
    def create_shipment(order, carrier, shipping_method, items_data=None):
        """
        Crear envío para una orden
        """
        # Calcular items si no se proporcionan
        if not items_data:
            items_data = [
                {'order_item': item, 'quantity': item.quantity}
                for item in order.items.all()
            ]
        
        shipment = Shipment.objects.create(
            order=order,
            carrier=carrier,
            shipping_method=shipping_method,
            shipping_address=order.shipping_address,
            shipping_cost=0  # Se actualiza según tarifa
        )
        
        # Crear ShipmentItems
        for item_data in items_data:
            ShipmentItem.objects.create(
                shipment=shipment,
                order_item=item_data['order_item'],
                quantity=item_data['quantity']
            )
        
        return shipment
    
    @staticmethod
    def generate_tracking(carrier):
        """
        Generar número de guía (mock o integración real)
        """
        import random
        import string
        
        if carrier == 'fedex':
            prefix = '1Z'
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            return f"{prefix}{suffix}"
        elif carrier == 'local':
            return f"LOC-{random.randint(100000, 999999)}"
        else:
            return f"TRK-{random.randint(100000000, 999999999)}"
    
    @staticmethod
    def update_tracking(shipment, tracking_number, status='shipped'):
        """
        Actualizar tracking y estado
        """
        from django.utils import timezone
        
        shipment.tracking_number = tracking_number
        shipment.status = status
        
        if status == 'shipped':
            shipment.shipped_at = timezone.now()
        elif status == 'delivered':
            shipment.delivered_at = timezone.now()
            # Actualizar orden
            shipment.order.update_status('delivered')
        
        shipment.save()
        return shipment

