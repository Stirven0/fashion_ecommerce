from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Category, Brand
from apps.inventory.models import InventoryLocation
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Inicializar datos básicos del sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando datos iniciales...')
        
        with transaction.atomic():
            self.create_categories()
            self.create_brands()
            self.create_inventory_locations()
            self.create_superuser()
        
        self.stdout.write(self.style.SUCCESS('Datos iniciales creados exitosamente'))
    
    def create_categories(self):
        categories = [
            {'name': 'Mujer', 'children': [
                {'name': 'Vestidos'},
                {'name': 'Blusas'},
                {'name': 'Pantalones'},
                {'name': 'Faldas'},
                {'name': 'Abrigos'},
            ]},
            {'name': 'Hombre', 'children': [
                {'name': 'Camisas'},
                {'name': 'Playeras'},
                {'name': 'Pantalones'},
                {'name': 'Chamarras'},
                {'name': 'Trajes'},
            ]},
            {'name': 'Accesorios', 'children': [
                {'name': 'Bolsas'},
                {'name': 'Zapatos'},
                {'name': 'Joyería'},
                {'name': 'Gorras'},
            ]},
        ]
        
        for cat_data in categories:
            parent, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'slug': self.slugify(cat_data['name'])}
            )
            
            for child_data in cat_data.get('children', []):
                Category.objects.get_or_create(
                    name=child_data['name'],
                    defaults={
                        'slug': self.slugify(child_data['name']),
                        'parent': parent
                    }
                )
        
        self.stdout.write('  ✓ Categorías creadas')
    
    def create_brands(self):
        brands = ['Zara', 'H&M', 'Mango', 'Pull & Bear', 'Bershka', 'Stradivarius', 'Massimo Dutti']
        
        for brand_name in brands:
            Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': self.slugify(brand_name)}
            )
        
        self.stdout.write('  ✓ Marcas creadas')
    
    def create_inventory_locations(self):
        locations = [
            'Bodega Central',
            'Tienda Centro',
            'Tienda Norte',
            'Centro de Distribución'
        ]
        
        for loc_name in locations:
            InventoryLocation.objects.get_or_create(name=loc_name)
        
        self.stdout.write('  ✓ Ubicaciones de inventario creadas')
    
    def create_superuser(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@fashionstore.com',
                password='admin123'  # Cambiar en producción
            )
            self.stdout.write('  ✓ Superusuario creado (admin/admin123)')
    
    def slugify(self, text):
        import unicodedata
        import re
        
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'[^\w\s-]', '', text).strip().lower()
        return re.sub(r'[-\s]+', '-', text)

