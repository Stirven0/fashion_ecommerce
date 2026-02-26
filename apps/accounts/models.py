from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from apps.core.models import TimeStampedModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Modelo de Usuario customizado usando el schema SQL proporcionado
    """
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(
        max_length=50, 
        unique=True, 
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username solo puede contener letras, números y guiones bajos.'
            )
        ]
    )
    email = models.EmailField(max_length=255, unique=True)
    email_verified = models.BooleanField(default=False)
    
    # Django required fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        if hasattr(self, 'profile'):
            return self.profile.full_name or self.username
        return self.username
    
    def get_short_name(self):
        return self.username


class CustomerProfile(TimeStampedModel):
    """
    Perfil de cliente extendido
    """
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        db_column='user_id'
    )
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    
    # Direcciones por defecto
    default_billing_address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_profiles',
        db_column='default_billing_address_id'
    )
    default_shipping_address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipping_profiles',
        db_column='default_shipping_address_id'
    )
    
    class Meta:
        db_table = 'customer_profiles'
        verbose_name = _('customer profile')
        verbose_name_plural = _('customer profiles')
    
    def __str__(self):
        return f"Profile: {self.full_name or self.user.email}"


class Address(TimeStampedModel):
    """
    Direcciones de usuarios
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='addresses',
        db_column='user_id'
    )
    label = models.CharField(max_length=50, blank=True, help_text="Ej: Casa, Oficina")
    recipient_name = models.CharField(max_length=255, blank=True)
    line1 = models.CharField(max_length=255, verbose_name="Dirección línea 1")
    line2 = models.CharField(max_length=255, blank=True, verbose_name="Dirección línea 2")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, verbose_name="Estado/Provincia")
    postal_code = models.CharField(max_length=30)
    country = models.CharField(max_length=100, default='México')
    phone = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'addresses'
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.label}: {self.line1}, {self.city}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'recipient_name': self.recipient_name,
            'line1': self.line1,
            'line2': self.line2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'phone': self.phone,
        }

