---
name: product-management
description: |
  Create, edit, and manage products and their variants via MCP tools.
  Includes category lookup, slug auto-generation, and stock management.
license: MIT
compatibility: opencode
metadata:
  audience: admin
  workflow: products
---

## Overview

Use this skill when the user asks to add, edit, or query products and variants.
Always list available categories first before creating a product.

## Context

- Products live in a hierarchy: Category → Product → ProductVariant
- Categories are pre-seeded (Ropa, Calzado, Accesorios + subcategories)
- Active categories have `is_active=True`
- Slugs are auto-generated from the product name (duplicates get `-1`, `-2`, etc.)
- Prices are in COP (Colombian Pesos), stored as integers
- `compare_price` is the "original" price for showing discounts (must be > price)

## MCP Tools

### List categories (via search or hardcoded)

Known categories from the seed migration:

| id | Name | Parent |
|----|------|--------|
| 1 | Ropa | — |
| 3 | Camisas | Ropa |
| 4 | Pantalones | Ropa |
| 2 | Camisetas | Ropa |
| 5 | Chaquetas | Ropa |
| 6 | Vestidos | Ropa |
| 7 | Sudaderas | Ropa |
| 8 | Calzado | — |
| 10 | Tenis | Calzado |
| 9 | Zapatos | Calzado |
| 11 | Sandalias | Calzado |
| 12 | Accesorios | — |
| 13 | Bolsos | Accesorios |
| 14 | Relojes | Accesorios |
| 15 | Gorras | Accesorios |
| 16 | Joyería | Accesorios |

*Always verify category IDs via `search_products` or by checking the response.*

### Create a product

Use `add_product(category_id, name, price, ...)`.

Required: `category_id`, `name`, `price`
Optional: `description`, `compare_price`, `has_variants`, `is_active`

The tool returns the created product with its `id`, `slug`, and `url`.

### Add a variant

Use `add_product_variant(product_id, size, color, stock, sku, ...)`.

Required: `product_id`
Optional: `size`, `color`, `color_code`, `stock`, `price_override`, `sku`, `is_active`

The combination of `size` + `color` must be unique per product.
Use `get_product_detail(product_id)` to verify after creation.

### Search & detail

- `search_products(query)` — find products by name
- `get_product_detail(product_id)` — full detail with variants and stock

## Conventions

- Confirm with the user before creating a product (show them the data)
- Always use `get_product_detail` to verify the product was created correctly
- For products with `has_variants=True`, always add at least one variant
- Variants with `stock=0` are still valid (shown as out of stock)
- If a slug conflicts, the system auto-appends a number
