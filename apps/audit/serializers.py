from rest_framework import serializers

from .models import AuditLog, SystemLog


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'username', 'action', 'action_display', 'severity', 'severity_display',
            'entity_type', 'entity_id', 'request_path', 'description',
            'ip_address', 'created_at'
        ]


class SystemLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemLog
        fields = ['id', 'level', 'module', 'message', 'created_at']

