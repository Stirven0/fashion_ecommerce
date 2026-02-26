from django.db import models
import uuid


class TimeStampedModel(models.Model):
    """Modelo abstracto con timestamps automáticos"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Modelo abstracto con UUID como PK"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Modelo abstracto con soft delete"""
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

