from rest_framework import serializers
from orders.models import SellerOrder

class SalesOverviewSerializer(serializers.Serializer):
    month = serializers.CharField()
    sales = serializers.IntegerField()

class SellerDashboardSerializers(serializers.Serializer):
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    revenue = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    processed_orders = serializers.IntegerField()
    shipped_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    completed_percentage = serializers.IntegerField()
    processed_percentage = serializers.IntegerField()
    shipped_percentage = serializers.IntegerField()
    pending_percentage = serializers.IntegerField()
    sales_overview = SalesOverviewSerializer(
        many=True
    )
    growth_percentage = serializers.FloatField()
    period = serializers.CharField()

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