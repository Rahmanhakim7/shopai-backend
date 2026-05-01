from django.db import models
from users.models import User
# Create your models here.
class Product(models.Model):
    seller = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'products'
    )
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
