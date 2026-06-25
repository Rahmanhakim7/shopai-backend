from django.urls import path
from .views import (
    CreateReviewAPIView,
    ProductReviewListAPIView
)

urlpatterns = [
    path(
        "order-items/<int:order_item_id>/",
        CreateReviewAPIView.as_view(),
        name="create-review",
    ),
    path(
        "product/<int:product_id>/",
        ProductReviewListAPIView.as_view(), 
        name="product-review"
    )
]