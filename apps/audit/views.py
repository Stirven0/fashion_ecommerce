from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q

from .models import AuditLog, SystemLog
from .serializers import AuditLogSerializer, SystemLogSerializer


class AuditLogListView(generics.ListAPIView):
    """
    Ver logs de auditoría (Admin only)
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = AuditLog.objects.select_related('user').all()
        
        # Filtros
        user_id = self.request.query_params.get('user')
        action = self.request.query_params.get('action')
        entity_type = self.request.query_params.get('entity_type')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        search = self.request.query_params.get('search')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(entity_type__icontains=search) |
                Q(request_path__icontains=search)
            )
        
        return queryset.order_by('-created_at')


class SystemLogListView(generics.ListAPIView):
    """
    Ver logs del sistema (Admin only)
    """
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = SystemLog.objects.all()
        
        level = self.request.query_params.get('level')
        module = self.request.query_params.get('module')
        
        if level:
            queryset = queryset.filter(level=level)
        if module:
            queryset = queryset.filter(module__icontains=module)
        
        return queryset.order_by('-created_at')[:1000]  # Limitar a últimos 1000


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def audit_stats(request):
    """
    Estadísticas de auditoría
    """
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Acciones en últimas 24 horas
    last_24h = timezone.now() - timedelta(hours=24)
    
    actions_24h = AuditLog.objects.filter(
        created_at__gte=last_24h
    ).values('action').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Entidades más modificadas
    top_entities = AuditLog.objects.values(        'entity_type'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Errores recientes
    recent_errors = SystemLog.objects.filter(
        level__in=['ERROR', 'CRITICAL'],
        created_at__gte=last_24h
    ).count()
    
    return Response({
        'actions_last_24h': list(actions_24h),
        'top_entities': list(top_entities),
        'errors_last_24h': recent_errors,
        'total_logs': AuditLog.objects.count()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def entity_history(request, entity_type, entity_id):
    """
    Historial completo de una entidad específica
    """
    logs = AuditLog.objects.filter(
        entity_type=entity_type,
        entity_id=entity_id
    ).select_related('user').order_by('-created_at')
    
    return Response({
        'entity_type': entity_type,
        'entity_id': entity_id,
        'history': AuditLogSerializer(logs, many=True).data
    })

