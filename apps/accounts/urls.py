from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, UserProfileView, 
    AddressListCreateView, AddressDetailView,
    set_default_address, change_password,
    CustomTokenObtainPairView
)

urlpatterns = [
    # Auth JWT
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration & Profile
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', change_password, name='change_password'),
    
    # Addresses
    path('addresses/', AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('addresses/<int:address_id>/set-default/<str:address_type>/', 
         set_default_address, name='set-default-address'),
]

