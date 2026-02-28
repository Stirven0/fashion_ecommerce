from django.urls import path

from .views import (
    CartDetailView, add_to_cart, update_cart_item,
    remove_from_cart, clear_cart, merge_cart_on_login, validate_cart
)

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart-detail'),
    path('add/', add_to_cart, name='cart-add'),
    path('update/', update_cart_item, name='cart-update'),
    path('remove/<int:variant_id>/', remove_from_cart, name='cart-remove'),
    path('clear/', clear_cart, name='cart-clear'),
    path('sync/', merge_cart_on_login, name='cart-sync'),
    path('validate/', validate_cart, name='cart-validate'),
]

