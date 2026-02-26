from django.urls import path

from .views import (
    AuditLogListView, SystemLogListView,
    audit_stats, entity_history
)

urlpatterns = [
    path('logs/', AuditLogListView.as_view(), name='audit-logs'),
    path('system-logs/', SystemLogListView.as_view(), name='system-logs'),
    path('stats/', audit_stats, name='audit-stats'),
    path('history/<str:entity_type>/<str:entity_id>/', entity_history, name='entity-history'),
]

