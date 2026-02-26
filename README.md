## Comandos para Iniciar el Proyecto
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 2. Instalar dependencias
pip install -r requirements/development.txt

# 3. Crear base de datos MySQL
mysql -u root -p -e "CREATE DATABASE fashion_ecommerce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 5. Crear migraciones y aplicar
python manage.py makemigrations accounts catalog inventory cart orders payments shipping discounts audit
python manage.py migrate

# 6. Crear datos iniciales
python manage.py init_data

# 7. Crear superusuario (si no se creó en init_data)
python manage.py createsuperuser

# 8. Iniciar servidor
python manage.py runserver

## Endpoints de la API Resumen
Módulo	Endpoint	Descripción	
Auth	`POST /api/v1/auth/register/`	Registro de usuario	
Auth	`POST /api/v1/auth/login/`	Login JWT	
Auth	`GET /api/v1/auth/profile/`	Perfil de usuario	
Auth	`GET/POST /api/v1/auth/addresses/`	CRUD direcciones	
Catalog	`GET /api/v1/catalog/categories/`	Listar categorías	
Catalog	`GET /api/v1/catalog/products/`	Listar productos (con filtros)	
Catalog	`GET /api/v1/catalog/products/{slug}/`	Detalle de producto	
Catalog	`GET /api/v1/catalog/products/filters/`	Opciones de filtro	
Inventory	`GET /api/v1/inventory/stock/`	Ver inventario	
Inventory	`GET /api/v1/inventory/check/{variant_id}/`	Verificar stock	
Cart	`GET /api/v1/cart/`	Ver carrito	
Cart	`POST /api/v1/cart/add/`	Agregar al carrito	
Cart	`PUT /api/v1/cart/update/`	Actualizar cantidad	
Cart	`DELETE /api/v1/cart/remove/{variant_id}/`	Eliminar item	
Orders	`POST /api/v1/orders/create/`	Crear orden	
Orders	`GET /api/v1/orders/`	Mis órdenes	
Orders	`GET /api/v1/orders/{id}/`	Detalle de orden	
Payments	`POST /api/v1/payments/`	Procesar pago	
Payments	`POST /api/v1/payments/webhooks/stripe/`	Webhook Stripe	
Shipping	`POST /api/v1/shipping/calculate/`	Calcular envío	
Shipping	`GET /api/v1/shipping/track/{tracking}/`	Rastrear envío	
Discounts	`POST /api/v1/discounts/validate/`	Validar cupón	
Discounts	`POST /api/v1/discounts/apply/`	Aplicar cupón	
Docs	`/api/docs/`	Swagger UI	
Docs	`/api/redoc/`	ReDoc	
___________________
✅ Arquitectura DDD modular
 
✅ API REST completa con documentación automática
 
✅ Autenticación JWT segura
 
✅ Gestión de inventario con reservas
 
✅ Carrito persistente (usuario y sesión)
 
✅ Flujo completo de checkout
 
✅ Integración de pagos (Stripe + offline)
 
✅ Sistema de envíos con tracking
 
✅ Cupones y promociones
 
✅ Auditoría completa
 
✅ Docker ready
 
✅ Escalable y mantenible


## Estructura Final del Proyecto
fashion_ecommerce/
├── apps/
│   ├── __init__.py
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── managers.py
│   │   ├── tests.py
│   │   └── admin.py
│   ├── catalog/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── admin.py
│   ├── inventory/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services.py
│   │   └── admin.py
│   ├── cart/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py
│   ├── orders/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services.py
│   │   └── admin.py
│   ├── payments/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py
│   ├── shipping/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py
│   ├── discounts/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py
│   ├── audit/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── middleware.py
│   │   └── utils.py
│   └── core/
│       ├── __init__.py
│       ├── models.py
│       ├── pagination.py
│       ├── exceptions.py
│       ├── utils.py
│       └── management/
│           └── commands/
│               └── init_data.py
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── requirements/
│   ├── base.txt
│   └── development.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── manage.py

