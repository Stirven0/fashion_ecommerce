# ruff: noqa: E402
from mcp.server.fastmcp import FastMCP

from .django_setup import setup_django

setup_django()

from .tools.analysis import get_full_report as _get_full_report
from .tools.analysis import get_sales_suggestions as _get_sales_suggestions
from .tools.kpi import get_kpis as _get_kpis
from .tools.kpi import get_revenue_trend as _get_revenue_trend
from .tools.orders import get_orders_by_status as _get_orders_by_status
from .tools.orders import get_pending_orders as _get_pending_orders
from .tools.orders import get_recent_orders as _get_recent_orders
from .tools.products import get_best_sellers as _get_best_sellers
from .tools.products import get_low_stock as _get_low_stock
from .tools.products import get_product_detail as _get_product_detail
from .tools.products import search_products as _search_products

mcp = FastMCP("Fashion Store Agent", json_response=True)

DESCRIPTION = (
    "Herramientas de administración para Fashion Store. "
    "Permite consultar KPIs, productos, pedidos, stock, ventas "
    "y obtener sugerencias para mejorar la tienda."
)
mcp.description = DESCRIPTION


@mcp.tool(description="KPIs generales de la tienda")
def get_dashboard_kpis() -> dict:
    return _get_kpis()


@mcp.tool(description="Top productos más vendidos por unidades")
def get_best_sellers(limit: int = 10) -> list[dict]:
    return _get_best_sellers(limit)


@mcp.tool(description="Variantes con stock bajo (≤ umbral)")
def get_low_stock(threshold: int = 5) -> list[dict]:
    return _get_low_stock(threshold)


@mcp.tool(description="Pedidos pendientes de confirmación WhatsApp")
def get_pending_orders() -> list[dict]:
    return _get_pending_orders()


@mcp.tool(description="Pedidos recientes (últimos N)")
def get_recent_orders(limit: int = 10) -> list[dict]:
    return _get_recent_orders(limit)


@mcp.tool(description="Filtrar pedidos por estado")
def get_orders_by_status(status: str | None = None) -> list[dict]:
    return _get_orders_by_status(status)


@mcp.tool(description="Ingresos diarios de los últimos N días")
def get_revenue_trend(days: int = 7) -> list[dict]:
    return _get_revenue_trend(days)


@mcp.tool(description="Buscar productos por nombre")
def search_products(query: str) -> list[dict]:
    return _search_products(query)


@mcp.tool(description="Detalle completo de un producto incluyendo variantes y stock")
def get_product_detail(product_id: int) -> dict | None:
    return _get_product_detail(product_id)


@mcp.tool(description="Sugerencias automáticas basadas en ventas, stock y pedidos")
def get_sales_suggestions() -> list[dict]:
    return _get_sales_suggestions()


@mcp.tool(description="Reporte completo de la tienda")
def get_full_report() -> dict:
    return _get_full_report()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
