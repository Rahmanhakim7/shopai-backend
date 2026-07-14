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
    has_review = serializers.SerializerMethodField()
    review_rating = serializers.SerializerMethodField()
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
            "has_review",
            "review_rating"
        ]
    
    def get_has_review(self, obj):
        return hasattr(obj, "review")

    def get_review_rating(self, obj):
        if hasattr(obj, "review"):
            return obj.review.rating
        return None

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
    payment_status = serializers.CharField(
        source="order.payment.status",
        read_only=True
    )
    class Meta:
        model = SellerOrder
        fields = [
            "id",
            "buyer_name",
            "seller_name",
            "payment_status",
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
    payment_status = serializers.CharField(
        source="payment.status",
        read_only=True,
    )
    class Meta:
        model = Order
        fields = [
            "id",
            "payment_status",
            "total_amount",
            "created_at",
            "seller_orders",
        ]

class CheckoutItemSerializer(
    serializers.Serializer
):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(
        min_value=1
    )


class CreateOrderSerializer(
    serializers.Serializer
):
    items = CheckoutItemSerializer(
        many=True
    )