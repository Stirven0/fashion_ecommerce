---
name: sales-analysis
description: |
  Analyze store performance: KPIs, best sellers, revenue trends,
  low stock alerts, and automated suggestions for improvement.
license: MIT
compatibility: opencode
metadata:
  audience: admin
  workflow: analysis
---

## Overview

Use this skill when the user asks about store performance, sales data,
inventory issues, or wants recommendations to improve the business.

## Key Metrics

All metrics are in COP (Colombian Pesos).

| KPI | Description |
|-----|-------------|
| Total products | All products (active + inactive) |
| Active products | Currently visible on the storefront |
| Total orders | All orders ever placed |
| Pending orders | Orders awaiting WhatsApp confirmation |
| Total revenue | Sum of all delivered/confirmed order totals |
| Low stock variants | Variants with stock ≤ 5 |
| Out of stock variants | Variants with stock = 0 |

## MCP Tools

### Quick overview

`get_dashboard_kpis()` — returns only the KPIs object.

### Full report

`get_full_report()` — returns everything in one call:
- `kpis` — metrics object
- `revenue_trend` — daily revenue for the last 7 days
- `pending_orders` — orders waiting confirmation
- `best_sellers` — products ranked by units sold
- `low_stock` — variants with low/zero stock
- `suggestions` — automated recommendations

### Individual analysis tools

| Tool | Use Case |
|---|---|
| `get_best_sellers(limit=10)` | Which products sell the most |
| `get_low_stock(threshold=5)` | What needs restocking |
| `get_revenue_trend(days=7)` | Daily sales chart data |
| `get_sales_suggestions()` | AI-generated improvement tips |

### Product deep-dive

- `get_product_detail(product_id)` — check individual product sales potential
- `search_products(query)` — find products by name

## Analysis Workflow

1. Start with `get_full_report()` for a complete picture
2. Drill down into specific areas:
   - Low stock → `get_low_stock()` → suggest restock priorities
   - Best sellers → `get_best_sellers()` → suggest featured placement
   - Pending orders → `get_pending_orders()` → suggest WhatsApp follow-up
   - Revenue trend → `get_revenue_trend()` → spot patterns
3. Review suggestions from `get_sales_suggestions()` and translate into actions

## Suggestions Interpretation

The `suggestions` array contains objects with:
- `type`: `critical`, `warning`, or `info`
- `area`: `inventario`, `pedidos`, `ventas`, `productos`
- `message`: human-readable recommendation

Prioritize `critical` → `warning` → `info`.
