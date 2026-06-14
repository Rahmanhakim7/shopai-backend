from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def total_price(self):
        return sum(item.quantity * item.price_at_added for item in self.items.all())
    def seller_totals(self):
        """
        return:
        {
            seller_id: total_price
        }
        """
        totals = {}
        for item in self.items.select_related("product__seller"):
            seller_id = item.product.seller_id
            totals[seller_id] = totals.get(seller_id, 0) + (
                item.quantity * item.price_at_added
            )
        return totals
    def __str__(self):
        return f"Cart - {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(
        "Cart",
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_added = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ["cart", "product"]
    def item_total(self):
        return self.quantity * self.price_at_added