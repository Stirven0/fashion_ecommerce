from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Categorías jerárquicas de productos
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        db_column='parent_id'
    )
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_full_path(self):
        """Retorna la ruta completa de categorías"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Brand(TimeStampedModel):
    """
    Marcas de productos
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    
    class Meta:
        db_table = 'brands'
        verbose_name = 'marca'
        verbose_name_plural = 'marcas'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    """
    Productos base
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        db_column='category_id'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        db_column='brand_id'
    )
    active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['active', 'category']),
            models.Index(fields=['active', 'brand']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})
    
    @property
    def main_image(self):
        """Retorna la imagen principal o la primera disponible"""
        main = self.images.filter(is_main=True).first()
        if main:
            return main
        return self.images.first()
    
    @property
    def has_variants(self):
        return self.variants.filter(active=True).exists()
    
    @property
    def min_price(self):
        """Precio mínimo entre variantes"""
        variants = self.variants.filter(active=True)
        if variants.exists():
            return min(v.price for v in variants)
        return self.base_price
    
    @property
    def max_price(self):
        """Precio máximo entre variantes"""
        variants = self.variants.filter(active=True)
        if variants.exists():
            return max(v.price for v in variants)
        return self.base_price


class ProductVariant(TimeStampedModel):
    """
    Variantes de productos (tallas, colores, etc.)
    """
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        db_column='product_id'
    )
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    size = models.CharField(max_length=50, blank=True, db_index=True)
    color = models.CharField(max_length=100, blank=True, db_index=True)
    attributes = models.JSONField(default=dict, blank=True, help_text="Atributos adicionales")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        db_table = 'product_variants'
        verbose_name = 'variante de producto'
        verbose_name_plural = 'variantes de productos'
        ordering = ['product', 'sku']
        indexes = [
            models.Index(fields=['product', 'active']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        attrs = f" - {self.size}/{self.color}" if self.size or self.color else ""
        return f"{self.product.name}{attrs} ({self.sku})"
    
    @property
    def total_stock(self):
        """Stock total en todas las ubicaciones"""
        from apps.inventory.models import Inventory
        inventories = Inventory.objects.filter(variant=self)
        return sum(inv.available_quantity for inv in inventories)


class ProductImage(TimeStampedModel):
    """
    Imágenes de productos y variantes
    """
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        db_column='product_id'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='images',
        db_column='variant_id'
    )
    image = models.ImageField(upload_to='products/%Y/%m/')
    is_main = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=255, blank=True, help_text="Texto alternativo para SEO")
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'product_images'
        verbose_name = 'imagen de producto'
        verbose_name_plural = 'imágenes de productos'
        ordering = ['sort_order', '-is_main', '-created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Si es imagen principal, desmarcar otras del mismo producto/variante
        if self.is_main:
            ProductImage.objects.filter(
                product=self.product,
                is_main=True
            ).exclude(id=self.id).update(is_main=False)
        super().save(*args, **kwargs)
    
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None

