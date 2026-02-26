from django.db import models
from django.contrib.auth import get_user_model

from apps.core.models import TimeStampedModel

User = get_user_model()


class AuditLog(TimeStampedModel):
    """
    Logs de auditoría de acciones importantes
    """
    ACTION_CHOICES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('PAYMENT', 'Proceso de Pago'),
        ('REFUND', 'Reembolso'),
        ('SHIP', 'Envío'),
        ('CANCEL', 'Cancelación'),
        ('VIEW', 'Visualización'),
        ('EXPORT', 'Exportación'),
    ]
    
    SEVERITY_CHOICES = [
        ('INFO', 'Informativo'),
        ('WARNING', 'Advertencia'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Crítico'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='INFO')
    
    # Contexto
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Entidad afectada
    entity_type = models.CharField(max_length=100, blank=True, help_text="Modelo afectado")
    entity_id = models.CharField(max_length=100, blank=True)
    
    # Datos
    previous_data = models.JSONField(default=dict, blank=True)
    new_data = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.entity_type} - {self.created_at}"


class SystemLog(TimeStampedModel):
    """
    Logs del sistema (errores, jobs, etc.)
    """
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    module = models.CharField(max_length=100)
    message = models.TextField()
    stack_trace = models.TextField(blank=True)
    context = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'system_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.level}] {self.module} - {self.message[:50]}"

