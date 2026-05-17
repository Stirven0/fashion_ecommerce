---
name: store-admin
description: |
  General store administration: migrations, superuser creation,
  data seeding, environment setup, and health checks.
license: MIT
compatibility: opencode
metadata:
  audience: admin
  workflow: setup
---

## Overview

Use this skill when the user asks about setting up, maintaining,
or checking the health of the store. Covers Django admin tasks,
database management, and environment configuration.

## Key Commands (run with `uv run`)

### Database

```bash
# Run migrations
python manage.py migrate

# Create migrations for an app
python manage.py makemigrations <app_name>

# Create superuser for dashboard access
python manage.py createsuperuser
```

### Dev Server

```bash
# Override DATABASE_URL for SQLite (no PostgreSQL in dev)
DATABASE_URL=sqlite:///db.sqlite3 uv run python manage.py runserver 0.0.0.0:8000
```

### Settings

- Development: `config.settings.local` (default)
- Production: `config.settings.production`
- Test: `config.settings.test` (pytest override)

Set via `DJANGO_SETTINGS_MODULE` env var or `--ds` flag.

### Context Processors (exposed to all templates)

- `store_settings` — `STORE_NAME`, `STORE_WHATSAPP`, `STORE_EMAIL`, `STORE_ADDRESS`, `STORE_CURRENCY`
- `cart_items` — `cart_items_count`
- `allauth_settings`

Configured in `config/settings/base.py`.

### Environment Variables

Key variables (defaults in `base.py`):

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `postgres:///fashion_store` | Override for dev: `sqlite:///db.sqlite3` |
| `REDIS_URL` | `redis://localhost:6379/0` | Used in production for cache |
| `STORE_NAME` | `Fashion Store` | |
| `STORE_WHATSAPP` | `+573001234567` | WhatsApp number for orders |
| `DJANGO_SECRET_KEY` | *(required in production)* | |

`.env` file is only loaded if `DJANGO_READ_DOT_ENV_FILE=True`.

## MCP Health Check

- `get_dashboard_kpis()` — quick health overview
- `get_full_report()` — comprehensive store health

## URLs

| Path | Purpose |
|---|---|
| `/admin/` | Django admin (full access) |
| `/dashboard/` | Staff dashboard (KPIs, product CRUD, order mgmt) |

## Seed Data

To populate the store with test data, use the seed script pattern:
```python
# Create categories, products, variants, orders
# See mcp_server/tools/products.py for the pattern
```

Categories are pre-seeded via migration `0002_seed_categories.py`.
