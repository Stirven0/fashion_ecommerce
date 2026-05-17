from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),
    path(
        "productos/",
        views.DashboardProductListView.as_view(),
        name="product_list",
    ),
    path(
        "productos/crear/",
        views.DashboardProductCreateView.as_view(),
        name="product_create",
    ),
    path(
        "productos/<int:pk>/editar/",
        views.DashboardProductUpdateView.as_view(),
        name="product_edit",
    ),
    path(
        "productos/<int:pk>/toggle/",
        views.dashboard_product_toggle_active,
        name="product_toggle",
    ),
    path(
        "pedidos/",
        views.DashboardOrderListView.as_view(),
        name="order_list",
    ),
    path(
        "pedidos/<int:pk>/",
        views.DashboardOrderDetailView.as_view(),
        name="order_detail",
    ),
    path(
        "pedidos/<int:pk>/status/",
        views.dashboard_order_update_status,
        name="order_status",
    ),
]
