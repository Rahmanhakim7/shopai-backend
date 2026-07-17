from django.urls import path
from .views import (
    MarkAllNotificationsReadAPIView,
    MarkNotificationReadAPIView,
    NotificationListAPIView,
    RecentNotificationAPIView,
    UnreadNotificationCountAPIView,
)

urlpatterns = [
    path("", NotificationListAPIView.as_view(), name="notification-list"),
    path("recent/", RecentNotificationAPIView.as_view(), name="notification-recent"),
    path(
        "unread-count/",
        UnreadNotificationCountAPIView.as_view(),
        name="notification-unread-count",
    ),
    path("<int:pk>/read/", MarkNotificationReadAPIView.as_view(), name="notification-read"),
    path("read-all/", MarkAllNotificationsReadAPIView.as_view(), name="notification-read-all"),
]