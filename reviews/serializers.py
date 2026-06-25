from rest_framework import serializers
from .models import Review

class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields =  [
            "rating",
            "comment"
        ]

class ReviewSerializer(serializers.ModelSerializer): 
    buyer_username = serializers.CharField(
        source="buyer.username",
        read_only = True
    )
    class Meta:
        model = Review
        fields = [
            "id",
            "buyer_username",
            "rating",
            "comment",
            "created_at"
        ]