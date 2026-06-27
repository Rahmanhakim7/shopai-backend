from django.db.models import Avg
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(
        source="seller.username",
        read_only=True
    )
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    wishlist_count = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["seller"]

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(
            avg=Avg("rating")
        )["avg"]

        return round(avg, 1) if avg else 0

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_wishlist_count(self, obj):
        return obj.wishlisted_by.count()