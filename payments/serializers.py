from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "transaction_id",
            "status",
            "payment_method",
            "amount",
            "snap_token",
            "payment_url",
            "created_at",
        ]

class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()