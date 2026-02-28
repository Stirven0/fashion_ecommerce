from django.urls import path

from .views import (
    create_payment, payment_detail, stripe_webhook,
    PaymentMethodListView, setup_payment_method
)

urlpatterns = [
    path('', create_payment, name='payment-create'),
    path('<int:payment_id>/', payment_detail, name='payment-detail'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    
    # Saved payment methods
    path('methods/', PaymentMethodListView.as_view(), name='payment-methods'),
    path('methods/setup/', setup_payment_method, name='payment-setup'),
]

