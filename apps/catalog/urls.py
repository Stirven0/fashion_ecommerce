from django.urls import path

from .views import (
    CategoryListView, CategoryDetailView,
    BrandListView, BrandDetailView,
    ProductListView, ProductDetailView,
    ProductVariantDetailView, get_available_filters
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Brands
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('brands/<slug:slug>/', BrandDetailView.as_view(), name='brand-detail'),
    
    # Products
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/filters/', get_available_filters, name='product-filters'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    
    # Variants
    path('variants/<int:pk>/', ProductVariantDetailView.as_view(), name='variant-detail'),
]

