from rest_framework import serializers
from orders.models import SellerOrder


class SellerDashboardSerializers(serializers.Serializer):
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    revenue = serializers.IntegerField()
    total_customers = serializers.IntegerField()


class RecentOrderSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id")
    customer = serializers.CharField(source="order.buyer.username")
    subtotal = serializers.IntegerField()
    status = serializers.CharField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = SellerOrder
        fields = [
            "order_id",
            "customer",
            "subtotal",
            "status",
            "products",
        ]

    def get_products(self, obj):
        return [
            item.product.name
            for item in obj.items.all()
        ] 