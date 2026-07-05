from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    profile_image = models.ImageField(
        upload_to = "users/profiles/",
        blank = True,
        null = True,
    )