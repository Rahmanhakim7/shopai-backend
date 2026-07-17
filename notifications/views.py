from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        notifications = (
            Notification.objects
            .filter(user=request.user)
            .order_by("-created_at")
        )
        notifications = (
            Notification.objects
            .filter(user=request.user)
            .order_by("-created_at")
        )

        serializer = NotificationSerializer(
            notifications,
            many=True,
        )

        return Response(
            {
                "unread_count": notifications.filter(
                    is_read=False
                ).count(),
                "notifications": serializer.data,
            }
        )


class RecentNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = (
            Notification.objects
            .filter(user=request.user)
            .order_by("-created_at")[:5]
        )

        serializer = NotificationSerializer(
            notifications,
            many=True,
        )

        return Response(serializer.data)


class UnreadNotificationCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()

        return Response(
            {
                "unread_count": unread_count
            }
        )


class MarkNotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user,
        )

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        serializer = NotificationSerializer(notification)

        return Response(
            {
                "message": "Notification marked as read.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class MarkAllNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request):
        updated = (
            Notification.objects
            .filter(
                user=request.user,
                is_read=False,
            )
            .update(is_read=True)
        )
        return Response(
            {
                "message": "All notifications marked as read.",
                "updated": updated,
            },
            status=status.HTTP_200_OK,
        )