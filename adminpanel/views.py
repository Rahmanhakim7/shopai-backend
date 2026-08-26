from datetime import date

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from products.models import Product
from orders.models import Order


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    if request.user.role != "admin":
        return Response(
            {
                "message": "Anda tidak memiliki akses ke dashboard admin."
            },
            status=403,
        )

    today = timezone.localdate()
    current_year = today.year
    current_month = today.month
    months = []

    for i in range(6, -1, -1):
        month = current_month - i
        year = current_year

        while month <= 0:
            month += 12
            year -= 1

        months.append(
            {
                "year": year,
                "month": month,
            }
        )

    first_month = months[0]

    start_date = date(
        first_month["year"],
        first_month["month"],
        1,
    )

    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "Mei",
        "Jun",
        "Jul",
        "Agu",
        "Sep",
        "Okt",
        "Nov",
        "Des",
    ]

    user_growth_query = (
        User.objects
        .filter(
            role__in=["buyer", "seller"],
            date_joined__gte=start_date,
        )
        .annotate(
            month=TruncMonth("date_joined")
        )
        .values(
            "month",
            "role",
        )
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    user_growth_map = {}

    for item in user_growth_query:
        month = item["month"]

        if not month:
            continue

        key = (
            month.year,
            month.month,
        )

        if key not in user_growth_map:
            user_growth_map[key] = {
                "buyers": 0,
                "sellers": 0,
            }

        if item["role"] == "buyer":
            user_growth_map[key]["buyers"] = item["total"]

        elif item["role"] == "seller":
            user_growth_map[key]["sellers"] = item["total"]

    order_growth_query = (
        Order.objects
        .filter(
            created_at__gte=start_date,
        )
        .annotate(
            month=TruncMonth("created_at")
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    order_growth_map = {}

    for item in order_growth_query:
        month = item["month"]

        if not month:
            continue

        key = (
            month.year,
            month.month,
        )

        order_growth_map[key] = item["total"]

    user_growth = []
    order_growth = []

    for item in months:
        key = (
            item["year"],
            item["month"],
        )

        user_data = user_growth_map.get(
            key,
            {
                "buyers": 0,
                "sellers": 0,
            },
        )

        user_growth.append(
            {
                "month": month_names[item["month"] - 1],
                "buyers": user_data["buyers"],
                "sellers": user_data["sellers"],
            }
        )

        order_growth.append(
            {
                "month": month_names[item["month"] - 1],
                "orders": order_growth_map.get(
                    key,
                    0,
                ),
            }
        )

    return Response(
        {
            "total_users": User.objects.count(),
            "total_sellers": User.objects.filter(
                role="seller"
            ).count(),
            "total_products": Product.objects.count(),
            "total_orders": Order.objects.count(),
            "user_growth": user_growth,
            "order_growth": order_growth,
        }
    )