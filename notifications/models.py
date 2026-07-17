from django.conf import settings
from django.db import models
from orders.models import Order,SellerOrder


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        NEW_ORDER = "new_order", "New Order"
        PAYMENT_SUCCESS = "payment_success", "Payment Success"
        ORDER_PROCESSED = "order_processed", "Order Processed"
        ORDER_SHIPPED = "order_shipped", "Order Shipped"
        ORDER_COMPLETED = "order_completed", "Order Completed"
        ORDER_CANCELLED = "order_cancelled", "Order Cancelled"
        
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    seller_order = models.ForeignKey(
        SellerOrder,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.user.username} - {self.title}"