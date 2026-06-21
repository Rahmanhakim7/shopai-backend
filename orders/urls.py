from django.urls import path
from .views import (
    CreateOrderAPIView,
    BuyerOrderListAPIView,
    BuyerOrderDetailAPIView,

    SellerOrderListAPIView,
    SellerOrderDetailAPIView,
    UpdateSellerOrderStatusAPIView,
)

urlpatterns = [
    path(
        "orders/create/",
        CreateOrderAPIView.as_view(),
        name="create-order"
    ),

    path(
        "orders/",
        BuyerOrderListAPIView.as_view(),
        name="buyer-order-list"
    ),

    path(
        "orders/<int:pk>/",
        BuyerOrderDetailAPIView.as_view(),
        name="buyer-order-detail"
    ),

    path(
        "seller/orders/",
        SellerOrderListAPIView.as_view(),
        name="seller-order-list"
    ),

    path(
        "seller/orders/<int:pk>/",
        SellerOrderDetailAPIView.as_view(),
        name="seller-order-detail"
    ),

    path(
        "seller/orders/<int:pk>/status/",
        UpdateSellerOrderStatusAPIView.as_view(),
        name="seller-order-status"
    ),
]