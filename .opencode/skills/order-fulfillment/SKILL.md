---
name: order-fulfillment
description: |
  Manage customer orders through the WhatsApp checkout flow.
  List pending orders, change statuses, and guide order fulfillment.
license: MIT
compatibility: opencode
metadata:
  audience: admin
  workflow: orders
---

## Overview

Use this skill when the user asks about orders, pending confirmations,
or needs to manage the order lifecycle from checkout to delivery.

## Order Statuses

| Status | Meaning |
|--------|---------|
| `pending_whatsapp` | Customer created order, awaiting WhatsApp confirmation |
| `confirmed` | Customer confirmed via WhatsApp |
| `processing` | Order is being prepared |
| `shipped` | Order has been dispatched |
| `delivered` | Successfully delivered |
| `cancelled` | Cancelled (by user or admin) |

## MCP Tools

### View pending orders

Use `get_pending_orders()` — shows orders with status `pending_whatsapp`.

Returns customer name, phone, total, items count, and creation time.

### Filter by status

Use `get_orders_by_status(status)` — pass any status from the table above.
Pass `null` to get all orders.

### Recent activity

Use `get_recent_orders(limit=10)` — latest orders regardless of status.

### Full analysis

Use `get_full_report()` — includes pending order count in the KPIs section
and suggestions about unconfirmed orders.

## WhatsApp Flow

1. Customer creates order via the web checkout (3-step: cart → shipping → confirm)
2. Order is created with status `pending_whatsapp`
3. Customer is redirected to `wa.me/<STORE_WHATSAPP>` with a pre-filled message
4. When customer confirms via WhatsApp, admin should manually update the order status
5. **The MCP tools are read-only for orders** — status changes must be done via the dashboard (`/dashboard/pedidos/`)

## Dashboard URL

- Order management: `/dashboard/pedidos/`
- Each order has an inline status change form
- Staff (not superuser) can access dashboard
