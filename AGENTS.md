# AGENTS.md

## Project

**fashion_store** — E-commerce Django app (Cookiecutter Django). Python 3.14, Django 6.0.3, package manager `uv`.

---

## Setup & Quickstart

```bash
uv sync
# dev server needs SQLite override (no PostgreSQL installed):
DATABASE_URL=sqlite:///db.sqlite3 uv run python manage.py runserver 0.0.0.0:8000
```

---

## Key commands (all prefixed with `uv run`)

| Command | Notes |
|---|---|
| `python manage.py migrate` | `manage.py` reads `DJANGO_SETTINGS_MODULE=config.settings.local` |
| `python manage.py makemigrations <app>` | **No `--ds` flag** — use `DJANGO_SETTINGS_MODULE=...` env instead |
| `python manage.py createsuperuser` | |
| `pytest` | Uses `--ds=config.settings.test --reuse-db --import-mode=importlib` (set in pyproject.toml) |
| `pytest tests/test_qa.py -v` | Run specific file |
| `pytest tests/test_qa.py -k "Wishlist"` | Filter by test name |
| `ruff check . && ruff format .` | Lint + format |
| `ruff check --fix .` | Auto-fix |
| `mypy fashion_store` | Typecheck |
| `djlint .` | Template lint |
| `python -m mcp_server` | Start MCP server (port 8100) — use `DATABASE_URL=sqlite:///db.sqlite3` |
| `python -m mcp_server --help` | MCP help |

Pre-commit: ruff check + format, djlint, django-upgrade (6.0), pyproject-fmt.

---

## Settings structure

`config/settings/` — `local.py` (default), `test.py` (pytest), `production.py`, `base.py` (shared).

Settings: `LANGUAGE_CODE = "es-co"`, `TIME_ZONE = "America/Bogota"`.

Context processors (`base.py`):
- `fashion_store.users.context_processors.allauth_settings`
- `fashion_store.context_processors.store_settings` — exposes `STORE_NAME`, `STORE_WHATSAPP`, `STORE_EMAIL`, `STORE_ADDRESS`, `STORE_CURRENCY` to templates
- `fashion_store.cart.context_processors.cart_items` — exposes `cart_items_count`

Store env vars: `STORE_NAME`, `STORE_WHATSAPP`, `STORE_EMAIL`, `STORE_ADDRESS`, `STORE_CURRENCY` (defaults in `base.py:294-298`).
`.env` only loaded if `DJANGO_READ_DOT_ENV_FILE=True`.

---

## Apps & ownership

| App | Path | What |
|---|---|---|
| `users` | `fashion_store/users/` | Custom User model, allauth integration, admin |
| `products` | `fashion_store/products/` | Category, Product, ProductVariant, ProductImage, ProductReview, WishlistItem + views/urls |
| `cart` | `fashion_store/cart/` | Session‑based Cart class, views (add/remove/update/detail), context processor |
| `orders` | `fashion_store/orders/` | Order, OrderItem, ShippingAddress; WhatsApp checkout; history |
| `dashboard` | `fashion_store/dashboard/` | Staff‑only panel: KPIs, product CRUD + variants, order management |
| `mcp_server` | `mcp_server/` | Standalone MCP server (FastMCP) — tools for KPIs, products, orders, sales analysis |
| Root views | `fashion_store/views.py` | HomeView (categories + featured products) |
| Root templates | `fashion_store/templates/` | base.html, allauth overrides, pages |
| `wishlist_views.py` | `fashion_store/products/wishlist_views.py` | Wishlist add/remove/detail views |

Test factories: `fashion_store/{users,products}/tests/factories.py`.  
Global fixture: `fashion_store/conftest.py` — `user` fixture, `_media_storage` (autouse, sets MEDIA_ROOT to tmpdir).

Migrations: excluded from ruff + mypy (set in pyproject.toml).

---

## MCP Server (`mcp_server/`)

Standalone FastMCP server. Tools (13 total):

### Consulta
- `get_dashboard_kpis`, `get_best_sellers`, `get_low_stock`, `get_pending_orders`
- `get_recent_orders`, `get_orders_by_status`, `get_revenue_trend`
- `search_products`, `get_product_detail`, `get_sales_suggestions`, `get_full_report`

### Administración
- `add_product(category_id, name, price, ...)` — crea producto con slug auto
- `add_product_variant(product_id, size, color, stock, sku, ...)` — agrega variante

Start: `DATABASE_URL=sqlite:///db.sqlite3 uv run python -m mcp_server`

---

## Deploy (Docker)

`docker-compose.yml` orquesta 5 servicios:

| Servicio | Puerto | Notas |
|---|---|---|
| `postgres` | 5432 | Volumen persistente |
| `redis` | 6379 | Cache/sesiones |
| `django` | 8000 (interno) | Gunicorn, migrate automático al iniciar |
| `mcp` | 8100 (interno) | MCP server vía Nginx en `/mcp` |
| `nginx` | 80 | Proxy reverso, static/media cacheado |

### Build & run

```bash
# Ajustar contraseñas primero
vim .envs/.production/.django .envs/.production/.postgres

docker compose build
docker compose up -d
docker compose exec django python manage.py createsuperuser
```

### Volúmenes

| Volumen | Mount |
|---|---|
| `postgres_data` | `/var/lib/postgresql/data` |
| `django_media` | `/app/media` |
| `django_static` | `/app/staticfiles` |

---

## Database

---

## Conventions

- **Ruff**: `force-single-line = true` (one import per line). Ignores `RUF012`, `S101`, `SIM102`.
- `@require_POST` for cart/wishlist mutating views. Login required via `@login_required`.
- **Wishlist**: POST to `products:wishlist_add` or `products:wishlist_remove`. GET `products:wishlist` for listing.
- **Checkout**: 3 steps (cart → shipping form → WhatsApp confirm). Order created before redirect to `wa.me/<number>`.
- **Cart** stored in `request.session` (no DB model). `CART_SESSION_ID = "cart"` in base settings.
