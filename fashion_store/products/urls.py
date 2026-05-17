from django.urls import path

from . import views
from . import wishlist_views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="list"),
    path("categorias/", views.CategoryListView.as_view(), name="categories"),
    path("categorias/<slug:slug>/", views.ProductListView.as_view(), name="category"),
    path("favoritos/", wishlist_views.wishlist_detail, name="wishlist"),
    path("favoritos/agregar/", wishlist_views.wishlist_add, name="wishlist_add"),
    path("favoritos/eliminar/", wishlist_views.wishlist_remove, name="wishlist_remove"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="detail"),
]
