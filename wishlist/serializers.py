from rest_framework import serializers
from .models import Wishlist

class WishlistSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(
        source="product.id",
        read_only=True
    )
    name = serializers.CharField(
        source="product.name",
        read_only=True
    )   
    price = serializers.IntegerField(
        source="product.price",
        read_only=True
    )
    stock = serializers.IntegerField(
        source="product.stock",
        read_only=True
    )
    condition = serializers.CharField(
        source="product.condition",
        read_only=True
    )
    image = serializers.ImageField(
        source="product.image",
        read_only=True
    )
    seller_name = serializers.CharField(
        source="product.seller.username",
        read_only=True
    )
    class Meta:
        model = Wishlist
        fields = [
            "id",
            "product_id",
            "name",
            "price",
            "stock",
            "condition",
            "image",
            "seller_name",
            "created_at",
        ]

class AddWishlistSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()