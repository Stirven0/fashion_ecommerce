import json
import time

from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware para logging automático de requests
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # No loggear media/static
        if request.path.startswith(('/static/', '/media/', '/admin/jsi18n/')):
            return response
        
        # Solo loggear métodos modificadores para usuarios autenticados
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and hasattr(request, 'user') and request.user.is_authenticated:
            try:
                self._create_audit_log(request, response)
            except Exception:
                # No fallar el request si el logging falla
                pass
        
        return response
    
    def _create_audit_log(self, request, response):
        """Crear registro de auditoría"""
        action = self._get_action(request.method)
        
        # Intentar determinar entidad afectada
        entity_type, entity_id = self._parse_entity_from_path(request.path)
        
        # Datos del request (limitar tamaño)
        try:
            body = json.loads(request.body) if request.body else {}
            # Remover datos sensibles
            body = self._sanitize_data(body)
        except Exception:
            body = {}
        
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=action,
            severity='INFO' if response.status_code < 400 else 'WARNING',
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            request_path=request.path[:500],
            request_method=request.method,
            entity_type=entity_type,
            entity_id=entity_id,
            new_data=body if action in ['CREATE', 'UPDATE'] else {},
            description=f"HTTP {response.status_code}"
        )
    
    def _get_action(self, method):
        mapping = {
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
        }
        return mapping.get(method, 'VIEW')
    
    def _parse_entity_from_path(self, path):
        """Intentar extraer tipo de entidad y ID del path"""
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            entity_type = parts[-2] if parts[-1].isdigit() else parts[-1]
            entity_id = parts[-1] if parts[-1].isdigit() else ''
            return entity_type, entity_id
        return '', ''
    
    def _sanitize_data(self, data):
        """Remover datos sensibles"""
        sensitive_fields = ['password', 'password_hash', 'cvv', 'card_number', 'token']
        if isinstance(data, dict):
            return {
                k: '***' if any(s in k.lower() for s in sensitive_fields) else v
                for k, v in data.items()
            }
        return data
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

