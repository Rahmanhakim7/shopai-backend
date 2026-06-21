from django.urls import path
from .views import (
    get_wishlist,
    add_to_wishlist,
    remove_wishlist
)

urlpatterns = [
    path(
        "",
        get_wishlist,
        name="wishlist-list"
    ),

    path(
        "add/",
        add_to_wishlist,
        name="wishlist-add"
    ),

    path(
        "<int:product_id>/",
        remove_wishlist,
        name="wishlist-remove"
    ),
]