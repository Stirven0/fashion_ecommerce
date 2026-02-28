from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Min, Max

from .models import Category, Brand, Product, ProductVariant
from .serializers import (
    CategorySerializer, BrandSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductVariantSerializer
)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class BrandDetailView(generics.RetrieveAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'


class ProductFilter:
    """Filtros personalizados para productos"""
    @staticmethod
    def filter_queryset(queryset, request):
        params = request.query_params
        
        # Filtro por categoría
        category = params.get('category')
        if category:
            # Incluir subcategorías
            try:
                cat = Category.objects.get(slug=category)
                descendants = [cat.id] + list(cat.children.all().values_list('id', flat=True))
                queryset = queryset.filter(category_id__in=descendants)
            except Category.DoesNotExist:
                queryset = queryset.filter(category__slug=category)
        
        # Filtro por marca
        brand = params.get('brand')
        if brand:
            queryset = queryset.filter(brand__slug=brand)
        
        # Filtro por precio
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        if min_price:
            queryset = queryset.filter(
                Q(base_price__gte=min_price) | 
                Q(variants__price__gte=min_price)
            ).distinct()
        if max_price:
            queryset = queryset.filter(
                Q(base_price__lte=max_price) | 
                Q(variants__price__lte=max_price)
            ).distinct()
        
        # Filtro por talla
        size = params.get('size')
        if size:
            queryset = queryset.filter(variants__size=size, variants__active=True).distinct()
        
        # Filtro por color
        color = params.get('color')
        if color:
            queryset = queryset.filter(variants__color=color, variants__active=True).distinct()
        
        # Búsqueda por texto
        search = params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search)
            ).distinct()
        
        return queryset


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        queryset = Product.objects.filter(active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images', 'variants')
        
        # Aplicar filtros
        queryset = ProductFilter.filter_queryset(queryset, self.request)
        
        # Ordenamiento
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'price_asc':
            queryset = queryset.annotate(min_variant_price=Min('variants__price'))
            queryset = queryset.order_by('min_variant_price', 'base_price')
        elif ordering == 'price_desc':
            queryset = queryset.annotate(max_variant_price=Max('variants__price'))
            queryset = queryset.order_by('-max_variant_price', '-base_price')
        else:
            queryset = queryset.order_by(ordering)
        
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(active=True).select_related(
        'category', 'brand'
    ).prefetch_related('images', 'variants', 'variants__images')
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'


class ProductVariantDetailView(generics.RetrieveAPIView):
    queryset = ProductVariant.objects.filter(active=True)
    serializer_class = ProductVariantSerializer


@api_view(['GET'])
def get_available_filters(request):
    """
    Endpoint para obtener filtros disponibles (tallas, colores, rangos de precio)
    """
    # Tallas únicas
    sizes = ProductVariant.objects.filter(
        active=True
    ).values_list('size', flat=True).distinct().exclude(size='').order_by('size')
    
    # Colores únicos
    colors = ProductVariant.objects.filter(
        active=True
    ).values_list('color', flat=True).distinct().exclude(color='').order_by('color')
    
    # Rango de precios
    from django.db.models import Min, Max
    price_stats = Product.objects.filter(active=True).aggregate(
        min_price=Min('base_price'),
        max_price=Max('base_price')
    )
    
    variant_prices = ProductVariant.objects.filter(active=True).aggregate(
        min_variant=Min('price'),
        max_variant=Max('price')
    )
    
    min_price = min(
        price_stats['min_price'] or 0,
        variant_prices['min_variant'] or 0
    )
    max_price = max(
        price_stats['max_price'] or 0,
        variant_prices['max_variant'] or 0
    )
    
    return Response({
        'sizes': list(sizes),
        'colors': list(colors),
        'price_range': {
            'min': float(min_price),
            'max': float(max_price)
        }
    })

