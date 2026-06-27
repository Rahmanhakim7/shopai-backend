from products.models import Product
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import SellerDashboardSerializers
from .serializers import RecentOrderSerializer
from orders.models import SellerOrder
from django.db.models import Sum

class SellerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.role != "seller":
            return Response(
                {"message": "Hanya seller yang dapat mengakses dashboard."},
                status=status.HTTP_403_FORBIDDEN
            )
        result = SellerOrder.objects.filter(
            seller=request.user,
            status="completed"
        ).aggregate(
            revenue=Sum("subtotal")
        )
        revenue = result["revenue"] or 0
        total_customers =  (
            SellerOrder.objects.filter(
                seller=request.user
            ).values("order__buyer").distinct().count()
        )
        data = {
            "total_products": Product.objects.filter(
                seller=request.user
            ).count(),
            "total_orders": SellerOrder.objects.filter(
                seller=request.user
            ).count(),
            "revenue": revenue,
            "total_customers": total_customers,
        }
        serializer = SellerDashboardSerializers(instance=data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RecentOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.role != "seller":
            return Response(
                {
                    "message": "Hanya seller yang dapat mengakses."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        orders = (
            SellerOrder.objects.filter(
                seller=request.user
            )
            .select_related(
                "order",
                "order__buyer"
            )
            .prefetch_related(
                "items__product"
            )
            .order_by("-created_at")[:2]
        )
        serializer = RecentOrderSerializer(
            orders,
            many=True
        )
        return Response(serializer.data)