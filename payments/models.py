from django.db import models
from orders.models import Order

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
    class PaymentMethod(models.TextChoices):
        MIDTRANS = "midtrans", "Midtrans"
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True
    )
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MIDTRANS
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    amount = models.PositiveIntegerField()
    snap_token = models.TextField(
        blank=True
    )
    payment_url = models.URLField(
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return (
            f"Payment #{self.id} "
            f"- Order #{self.order.id}"
        )