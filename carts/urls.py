from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.get_cart,
        name="get-cart"
    ),

    path(
        "add/",
        views.add_to_cart,
        name="add-to-cart"
    ),

    path(
        "items/<int:cart_item_id>/",
        views.cart_item_detail,
        name="cart-item-detail"
    ),
]