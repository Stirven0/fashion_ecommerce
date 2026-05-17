# Fashion Store

Tienda de moda online con carrito de compras, catálogo de productos, pedidos vía WhatsApp y panel de administración.

## Stack

- **Django 6.0.3** / **Python 3.14**
- **Bootstrap 5** (frontend)
- **django-allauth** (autenticación)
- **SQLite** (desarrollo) / **PostgreSQL** (producción)
- **WhatsApp** (confirmación de pedidos vía `wa.me`)

## Funcionalidades

- Catálogo de productos con variantes (talla + color), imágenes y reseñas
- Carrito de compras en sesión (sin registro)
- Checkout 3 pasos: carrito → datos envío → confirmación por WhatsApp
- Historial de pedidos por usuario
- Lista de deseos (favoritos)
- Panel de administración en `/dashboard/` (staff-only) con KPIs, CRUD de productos y gestión de pedidos
- Categorías jerárquicas con precarga inicial
- Búsqueda y filtros (categoría, precio, talla, color)
- Temas: idioma español (`es-co`), moneda COP

## Inicio rápido

```bash
uv sync
DATABASE_URL=sqlite:///db.sqlite3 uv run python manage.py migrate
DATABASE_URL=sqlite:///db.sqlite3 uv run python manage.py runserver 0.0.0.0:8000
```

### Crear superusuario (para acceder al dashboard)

```bash
DATABASE_URL=sqlite:///db.sqlite3 uv run python manage.py createsuperuser
```

Luego ingresa a `http://localhost:8000/dashboard/`.

## Rutas principales

| URL | Descripción |
|---|---|
| `/` | Portada con categorías y productos destacados |
| `/productos/` | Catálogo con filtros y búsqueda |
| `/productos/<slug>/` | Detalle de producto |
| `/carrito/` | Carrito de compras |
| `/pedidos/checkout/` | Checkout paso 1 (datos de envío) |
| `/pedidos/checkout/confirmar/` | Confirmación y enlace WhatsApp |
| `/pedidos/historial/` | Historial de pedidos del usuario |
| `/favoritos/` | Lista de deseos |
| `/dashboard/` | Panel de administración (staff) |
| `/admin/` | Django admin |
| `/accounts/` | Autenticación (allauth) |

## Tests

```bash
uv run pytest
```

79 tests (funcionales + no funcionales: rendimiento, seguridad, consultas, integridad, templates).

## Variables de entorno

| Variable | Default |
|---|---|
| `DATABASE_URL` | `postgres:///fashion_store` |
| `STORE_NAME` | `Fashion Store` |
| `STORE_WHATSAPP` | `+573001234567` |
| `STORE_EMAIL` | `hola@fashionstore.com` |
| `STORE_ADDRESS` | *(vacío)* |
| `STORE_CURRENCY` | `COP` |

## Licencia

Apache Software License 2.0
