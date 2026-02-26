from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import CustomerProfile, Address

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'label', 'recipient_name', 'line1', 'line2',
            'city', 'state', 'postal_code', 'country', 'phone', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CustomerProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    default_billing_address = AddressSerializer(read_only=True)
    default_shipping_address = AddressSerializer(read_only=True)
    
    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'full_name', 'phone', 
            'default_billing_address', 'default_shipping_address',
            'addresses', 'created_at', 'updated_at'
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'email_verified',
            'is_active', 'date_joined', 'created_at', 'profile'
        ]
        read_only_fields = ['id', 'email_verified', 'date_joined', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'full_name', 'phone']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        # Remover campos del perfil
        full_name = validated_data.pop('full_name', '')
        phone = validated_data.pop('phone', '')
        validated_data.pop('password_confirm')
        
        # Crear usuario
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Crear perfil automáticamente
        CustomerProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone
        )
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = CustomerProfileSerializer()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'profile']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Actualizar usuario
        instance.username = validated_data.get('username', instance.username)
        instance.save()
        
        # Actualizar perfil
        profile = instance.profile
        profile.full_name = profile_data.get('full_name', profile.full_name)
        profile.phone = profile_data.get('phone', profile.phone)
        profile.save()
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden")
        return data

