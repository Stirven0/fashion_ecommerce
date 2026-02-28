from rest_framework import serializers

from .models import Category, Brand, Product, ProductVariant, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'children', 'full_path']
    
    def get_children(self, obj):
        if hasattr(obj, 'children'):
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo']


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_main', 'alt_text', 'sort_order']


class ProductVariantSerializer(serializers.ModelSerializer):
    stock = serializers.IntegerField(source='total_stock', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'size', 'color', 'attributes',
            'price', 'active', 'stock', 'images'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    main_image = ProductImageSerializer(read_only=True)
    price_range = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'base_price', 'category', 'category_name',
            'brand', 'brand_name', 'active', 'main_image', 'price_range'
        ]
    
    def get_price_range(self, obj):
        if obj.has_variants:
            return {
                'min': obj.min_price,
                'max': obj.max_price
            }
        return {'min': obj.base_price, 'max': obj.base_price}


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    price_range = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'base_price',
            'category', 'brand', 'active', 'images', 'variants',
            'price_range', 'created_at', 'updated_at'
        ]
    
    def get_price_range(self, obj):
        if obj.has_variants:
            return {
                'min': obj.min_price,
                'max': obj.max_price
            }
        return {'min': obj.base_price, 'max': obj.base_price}

