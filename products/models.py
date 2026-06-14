from django.db import models
from users.models import User

class Product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('sold_out', 'Sold Out'),
    )
    CONDITION_CHOICES = (
        ("new", "Baru"),
        ("used", "Bekas"),
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    stock = models.PositiveBigIntegerField(default=0)
    condition = models.CharField(
        max_length=10,
        choices=CONDITION_CHOICES,
        default='new'
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
