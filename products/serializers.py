from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    wishlist_count = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['seller']
    def get_wishlist_count(self, obj):
        return obj.wishlisted_by.count()    
