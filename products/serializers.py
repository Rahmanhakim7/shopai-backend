from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['seller']
