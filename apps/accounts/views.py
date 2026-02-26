from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Address, CustomerProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserUpdateSerializer,
    AddressSerializer, PasswordChangeSerializer, CustomerProfileSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Usuario registrado exitosamente. Por favor verifica tu email.'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_default_address(request, address_id, address_type):
    """
    Establecer dirección por defecto (billing o shipping)
    """
    user = request.user
    address = get_object_or_404(Address, id=address_id, user=user)
    profile = user.profile
    
    if address_type == 'billing':
        profile.default_billing_address = address
    elif address_type == 'shipping':
        profile.default_shipping_address = address
    else:
        return Response(
            {'error': 'Tipo de dirección inválido. Use billing o shipping'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    profile.save()
    return Response({
        'message': f'Dirección {address_type} por defecto actualizada',
        'address': AddressSerializer(address).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Contraseña actual incorrecta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Contraseña actualizada exitosamente'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# JWT Personalizado
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get('email'))
            response.data['user'] = UserSerializer(user).data
            
        return response

