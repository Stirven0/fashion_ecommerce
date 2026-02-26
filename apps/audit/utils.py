import logging
import traceback

from .models import AuditLog, SystemLog


logger = logging.getLogger('fashion_ecommerce')


class AuditHelper:
    """
    Helper para crear logs de auditoría manualmente desde servicios
    """
    
    @staticmethod
    def log_action(user, action, entity_type, entity_id, 
                   previous_data=None, new_data=None, description=""):
        """
        Crear log de auditoría manual
        """
        try:
            return AuditLog.objects.create(
                user=user,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id),
                previous_data=previous_data or {},
                new_data=new_data or {},
                description=description
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            return None
    
    @staticmethod
    def log_system_error(module, message, exception=None, context=None):
        """
        Log de error del sistema
        """
        stack_trace = ""
        if exception:
            stack_trace = traceback.format_exc()
        
        try:
            return SystemLog.objects.create(
                level='ERROR',
                module=module,
                message=message,
                stack_trace=stack_trace[:2000],  # Limitar tamaño
                context=context or {}
            )
        except Exception as e:
            logger.error(f"Failed to create system log: {e}")
            return None
    
    @staticmethod
    def log_payment(user, order, amount, status, provider, description=""):
        """
        Log específico para pagos
        """
        return AuditHelper.log_action(
            user=user,
            action='PAYMENT',
            entity_type='order',
            entity_id=order.id,
            new_data={
                'amount': str(amount),
                'status': status,
                'provider': provider
            },
            description=description or f"Pago {status} por ${amount}"
        )

