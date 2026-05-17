# Fashion Store

Tienda de moda online con carrito de compras, catálogo de productos, pedidos vía WhatsApp y panel de administración.

## Stack

- **Django 6.0.3** / **Python 3.14**
- **Bootstrap 5** (frontend)
- **django-allauth** (autenticación)
- **SQLite** (desarrollo) / **PostgreSQL** (producción)
- **WhatsApp** (confirmación de pedidos vía `wa.me`)
- **MCP Server** (asistente IA para administración de la tienda — compatible con Claude Desktop, Hermes Agent, OpenCode)
- **Docker** (producción: postgres + redis + gunicorn + nginx + MCP)

## Funcionalidades

- Catálogo de productos con variantes (talla + color), imágenes y reseñas
- Carrito de compras en sesión (sin registro)
- Checkout 3 pasos: carrito → datos envío → confirmación por WhatsApp
- Historial de pedidos por usuario
- Lista de deseos (favoritos)
- Panel de administración en `/dashboard/` (staff-only) con KPIs, CRUD de productos y gestión de pedidos
- Categorías jerárquicas con precarga inicial
- Búsqueda y filtros (categoría, precio, talla, color)
- Asistente IA vía MCP: consultar KPIs, productos, pedidos, stock, ventas, y administrar la tienda
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

## MCP Server

Servidor MCP (Model Context Protocol) para que asistentes IA puedan administrar la tienda. Corre en `localhost:8100` y expone 13 herramientas:

### Herramientas de consulta

| Tool | Descripción |
|---|---|
| `get_dashboard_kpis` | KPIs generales (productos, pedidos, ingresos, stock) |
| `get_best_sellers` | Top productos más vendidos |
| `get_low_stock` | Variantes con stock bajo o agotado |
| `get_pending_orders` | Pedidos pendientes de confirmación WhatsApp |
| `get_recent_orders` | Pedidos recientes (últimos N) |
| `get_orders_by_status` | Filtrar pedidos por estado |
| `get_revenue_trend` | Ingresos diarios (últimos N días) |
| `search_products` | Buscar productos por nombre |
| `get_product_detail` | Detalle completo de producto con variantes y stock |
| `get_sales_suggestions` | Sugerencias automáticas basadas en ventas, stock y pedidos |
| `get_full_report` | Reporte completo de la tienda |

### Herramientas de administración

| Tool | Descripción |
|---|---|
| `add_product` | Crear un nuevo producto (categoría, nombre, precio, descripción, etc.) |
| `add_product_variant` | Agregar variante (talla/color) a un producto existente |

### Iniciar MCP Server

```bash
DATABASE_URL=sqlite:///db.sqlite3 uv run python -m mcp_server
```

### Despliegue Docker

```bash
docker compose build
docker compose up -d
docker compose exec django python manage.py createsuperuser
```

Nginx expone en puerto 80. Ver `.envs/.production/` para configuración.

### Integración con OpenCode

Agregar en `opencode.json`:

```json
{
  "mcpServers": {
    "fashion_store": {
      "type": "url",
      "url": "http://localhost:8100/mcp"
    }
  }
}
```

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
