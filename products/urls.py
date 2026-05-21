from django.urls import path
from .views import (
    product_list,
    product_detail,
    seller_products,
    seller_product_detail)

urlpatterns = [
    path(
        'products/',
        product_list,
        name='product-list'
    ),
    path(
        'products/<int:pk>/',
        product_detail,
        name='product-detail'
    ),
    path(
        'seller/products/',
        seller_products,
        name='seller-products'
    ),
    path(
        'seller/products/<int:pk>/',
        seller_product_detail,
        name='seller-product-detail'
    ),
]
