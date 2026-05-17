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
| Root views | `fashion_store/views.py` | HomeView (categories + featured products) |
| Root templates | `fashion_store/templates/` | base.html, allauth overrides, pages |
| `wishlist_views.py` | `fashion_store/products/wishlist_views.py` | Wishlist add/remove/detail views |

Test factories: `fashion_store/{users,products}/tests/factories.py`.  
Global fixture: `fashion_store/conftest.py` — `user` fixture, `_media_storage` (autouse, sets MEDIA_ROOT to tmpdir).

Migrations: excluded from ruff + mypy (set in pyproject.toml).

---

## Database

`DATABASE_URL` env var (default `postgres:///fashion_store`). This environment has no PostgreSQL — always override:
```
DATABASE_URL=sqlite:///db.sqlite3
```
Test uses SQLite via env override in `config/settings/test.py`.

---

## Conventions

- **Ruff**: `force-single-line = true` (one import per line). Ignores `RUF012`, `S101`, `SIM102`.
- `@require_POST` for cart/wishlist mutating views. Login required via `@login_required`.
- **Wishlist**: POST to `products:wishlist_add` or `products:wishlist_remove`. GET `products:wishlist` for listing.
- **Checkout**: 3 steps (cart → shipping form → WhatsApp confirm). Order created before redirect to `wa.me/<number>`.
- **Cart** stored in `request.session` (no DB model). `CART_SESSION_ID = "cart"` in base settings.
