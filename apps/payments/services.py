import stripe
from django.conf import settings
from django.db import transaction

from .models import Payment


class StripeService:
    """
    Servicio de integración con Stripe
    """
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def create_payment_intent(self, payment, return_url=None):
        """
        Crear PaymentIntent en Stripe
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Stripe usa centavos
                currency='mxn',
                metadata={
                    'order_id': payment.order_id,
                    'payment_id': payment.id
                },
                automatic_payment_methods={'enabled': True}
            )
            
            payment.provider = 'stripe'
            payment.provider_payment_id = intent.id
            payment.provider_response = {'client_secret': intent.client_secret}
            payment.status = 'processing'
            payment.save()
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
            
        except stripe.error.StripeError as e:
            payment.mark_as_failed(str(e))
            raise
    
    def confirm_payment(self, payment_intent_id):
        """Verificar estado de pago en Stripe"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent
        except stripe.error.StripeError:
            return None


class PaymentService:
    """
    Servicio general de pagos
    """
    
    @staticmethod
    @transaction.atomic
    def create_payment(order, method, **kwargs):
        """
        Crear registro de pago y procesar según método
        """
        # Verificar que no haya pagos completados
        if order.payments.filter(status='completed').exists():
            raise ValueError("La orden ya tiene un pago completado")
        
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            method=method,
            status='pending'
        )
        
        # Procesar según método
        if method in ['credit_card', 'debit_card', 'stripe']:
            stripe_service = StripeService()
            result = stripe_service.create_payment_intent(payment)
            return {
                'payment': PaymentSerializer(payment).data,
                'processor_data': result
            }
        
        elif method in ['oxxo', 'spei']:
            # Pagos offline - generar referencia
            payment.status = 'pending'
            payment.save()
            return {
                'payment': PaymentSerializer(payment).data,
                'instructions': PaymentService.get_offline_instructions(method, payment)
            }
        
        elif method == 'cash_on_delivery':
            payment.status = 'pending'
            payment.save()
            return {
                'payment': PaymentSerializer(payment).data,
                'message': 'Pago contra entrega registrado'
            }
        
        return {'payment': PaymentSerializer(payment).data}
    
    @staticmethod
    def get_offline_instructions(method, payment):
        """Generar instrucciones para pagos offline"""
        if method == 'oxxo':
            # Generar código de barras OXXO
            return {
                'barcode': f'0000{payment.id:010d}',
                'reference': f'OXXO-{payment.id}',
                'expires_at': '24 horas',
                'instructions': 'Acude a cualquier tienda OXXO y realiza tu pago'
            }
        elif method == 'spei':
            return {
                'clabe': f'000123456789012345{payment.id:04d}',
                'reference': f'SPEI-{payment.id}',
                'bank': 'STP'
            }
        return {}
    
    @staticmethod
    def process_webhook(provider, payload):
        """
        Procesar webhook de procesador de pagos
        """
        if provider == 'stripe':
            return PaymentService._process_stripe_webhook(payload)
        return False
    
    @staticmethod
    def _process_stripe_webhook(payload):
        """Procesar webhook de Stripe"""
        event = payload.get('type')
        data = payload.get('data', {}).get('object', {})
        
        if event == 'payment_intent.succeeded':
            payment_intent_id = data.get('id')
            try:
                payment = Payment.objects.get(
                    provider_payment_id=payment_intent_id,
                    provider='stripe'
                )
                payment.mark_as_completed(data)
                return True
            except Payment.DoesNotExist:
                return False
        
        elif event == 'payment_intent.payment_failed':
            payment_intent_id = data.get('id')
            error = data.get('last_payment_error', {}).get('message', 'Unknown error')
            try:
                payment = Payment.objects.get(
                    provider_payment_id=payment_intent_id,
                    provider='stripe'
                )
                payment.mark_as_failed(error)
                return True
            except Payment.DoesNotExist:
                return False
        
        return False

