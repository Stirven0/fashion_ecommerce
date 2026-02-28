from django.urls import path

from .views import (
    validate_coupon, apply_coupon_to_order,
    PromotionListView, CouponAdminView
)

urlpatterns = [
    path('validate/', validate_coupon, name='coupon-validate'),
    path('apply/', apply_coupon_to_order, name='coupon-apply'),
    path('promotions/', PromotionListView.as_view(), name='promotion-list'),
    
    # Admin
    path('admin/coupons/', CouponAdminView.as_view(), name='admin-coupons'),
]

