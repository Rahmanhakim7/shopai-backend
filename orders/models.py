from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    total_amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return f"Order #{self.id} - {self.buyer.username}"

class SellerOrder(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processed", "Processed"),
        ("shipped", "Shipped"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="seller_orders"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="seller_orders"
    )
    subtotal = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return (
            f"Order #{self.order.id} "
            f"- Seller {self.seller.username}"
        )

class OrderItem(models.Model):
    seller_order = models.ForeignKey(
        SellerOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    def __str__(self):
        return (
            f"{self.product.name} "
            f"x {self.quantity}"
        )