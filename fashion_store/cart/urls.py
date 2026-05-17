from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="detail"),
    path("agregar/", views.cart_add, name="add"),
    path("eliminar/", views.cart_remove, name="remove"),
    path("actualizar/", views.cart_update, name="update"),
]
