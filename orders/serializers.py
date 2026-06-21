from rest_framework import serializers
from .models import (
    Order,
    SellerOrder,
    OrderItem,
)
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )
    product_image = serializers.ImageField(
        source="product.image",
        read_only=True
    )
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "quantity",
            "price",
            "subtotal",
        ]

class SellerOrderSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(
        source="seller.username",
        read_only=True
    )
    buyer_name = serializers.CharField(
        source="order.buyer.username",
        read_only=True
    )
    items = OrderItemSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = SellerOrder
        fields = [
            "id",
            "buyer_name",
            "seller_name",
            "status",
            "subtotal",
            "created_at",
            "items",
        ]
class OrderSerializer(serializers.ModelSerializer):
    seller_orders = SellerOrderSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = Order
        fields = [
            "id",
            "total_amount",
            "created_at",
            "seller_orders",
        ]

class CreateOrderSerializer(serializers.Serializer):
    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )