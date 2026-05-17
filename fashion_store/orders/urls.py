from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout_step1, name="checkout_step1"),
    path("checkout/confirmar/", views.checkout_step2, name="checkout_step2"),
    path("historial/", views.order_history, name="history"),
    path("<int:order_id>/", views.order_detail, name="detail"),
]
