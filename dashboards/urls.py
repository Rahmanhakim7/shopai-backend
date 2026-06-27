from django.urls import path
from .views import SellerDashboardAPIView
from .views import RecentOrderAPIView

urlpatterns = [
    path(
        "dashboards/",
        SellerDashboardAPIView.as_view(),
        name="seller-dashboards"
    ),
    path(
        "recent-orders/",
        RecentOrderAPIView.as_view(),
        name="recent-orders",
    ),
]