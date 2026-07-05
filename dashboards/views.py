from products.models import Product
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import SellerDashboardSerializers
from .serializers import RecentOrderSerializer
from orders.models import SellerOrder
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from calendar import month_abbr
from datetime import date
from django.utils import timezone

class SellerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.role != "seller":
            return Response(
                {
                    "message": "Hanya seller yang dapat mengakses dashboard."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        result = SellerOrder.objects.filter(
            seller=request.user,
            status="completed"
        ).aggregate(
            revenue=Sum("subtotal")
        )
        revenue = result["revenue"] or 0
        total_customers = (
            SellerOrder.objects.filter(
                seller=request.user
            )
            .values("order__buyer")
            .distinct()
            .count()
        )
        seller_orders = SellerOrder.objects.filter(
            seller=request.user
        )
        total_orders = seller_orders.count()
        completed_orders = seller_orders.filter(
            status="completed"
        ).count()
        shipped_orders = seller_orders.filter(
            status="shipped"
        ).count()
        processed_orders = seller_orders.filter(
            status="processed"
        ).count()
        pending_orders = seller_orders.filter(
            status="pending"
        ).count()

        def get_percentage(value,total):
            if total == 0:
                return 0
            return round((value/total) * 100)

        completed_percentage = get_percentage(completed_orders,total_orders)
        shipped_percentage = get_percentage(shipped_orders,total_orders)
        processed_percentage = get_percentage(processed_orders,total_orders)
        pending_percentage = get_percentage(pending_orders,total_orders)

        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        last_month_end = current_month_start - timezone.timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        current_month_revenue = (
            SellerOrder.objects.filter(
                seller=request.user,
                status="completed",
                created_at__date__gte=current_month_start,
            )
            .aggregate(total=Sum("subtotal"))
        )["total"] or 0
        last_month_revenue = (
            SellerOrder.objects.filter(
                seller=request.user,
                status="completed",
                created_at__date__gte=last_month_start,
                created_at__date__lte=last_month_end,
            )
            .aggregate(total=Sum("subtotal"))
        )["total"] or 0
        if last_month_revenue > 0:
            growth_percentage = (
                (current_month_revenue - last_month_revenue)
                / last_month_revenue
            ) * 100
        elif current_month_revenue > 0:
            growth_percentage = 100
        else:
            growth_percentage = 0

        sales_overview = (
            SellerOrder.objects.filter(
                seller=request.user,
                status="completed"
            ).annotate(
                month=TruncMonth("created_at")
            ).values("month")
            .annotate(
                sales=Sum("subtotal")
            )
            .order_by("month")
        )
        sales_map = {
            item["month"].month: item["sales"]
            for item in sales_overview
        }
        sales_chart = [
            {
                "month": month_abbr[i],
                "sales": sales_map.get(i,0),
            }
            for i in range(1,13)
        ]  
        period = f"January {today.year} - {today.strftime('%B')} {today.year}"   
        data = {
            "total_products": Product.objects.filter(
                seller=request.user
            ).count(),
            "total_orders": SellerOrder.objects.filter(
                seller=request.user
            ).count(),
            "revenue": revenue,
            "total_customers": total_customers,
            "sales_overview": sales_chart,
            "growth_percentage": round(growth_percentage, 1),
            "period": period,
            "completed_orders": completed_orders,
            "processed_orders": processed_orders,
            "shipped_orders": shipped_orders,
            "pending_orders": pending_orders,
            "completed_percentage": completed_percentage,
            "processed_percentage": processed_percentage,
            "shipped_percentage": shipped_percentage,
            "pending_percentage": pending_percentage,
        }
        serializer = SellerDashboardSerializers(
            instance=data
        )
        return Response(serializer.data)
    
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