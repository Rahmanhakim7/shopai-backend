from django.urls import path
from .views import (
    WishlistListView,
    add_to_wishlist,
    remove_wishlist,
)

urlpatterns = [
    path(
        "",
        WishlistListView.as_view(),
        name="wishlist",
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