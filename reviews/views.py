from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from orders.models import OrderItem
from products.models import Product

from .models import Review
from .serializers import CreateReviewSerializer
from .serializers import ReviewSerializer

class CreateReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, order_item_id):
        try:
            order_item = OrderItem.objects.get(
                id=order_item_id
            )
        except OrderItem.DoesNotExist:
            return Response(
                {
                    "message": "Order item tidak ditemukan"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if order_item.seller_order.order.buyer != request.user:
            return Response(
                {
                    "message": "Anda tidak bisa review produk ini"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        if order_item.seller_order.status != "completed":
            return Response(
                {
                    "message": "Pesanan belum selesai"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if hasattr(order_item, "review"):
            return Response(
                {
                    "message": "Produk ini sudah direview"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CreateReviewSerializer(
            data=request.data
        )
        if serializer.is_valid():
            review = Review.objects.create(
                order_item=order_item,
                product=order_item.product,
                buyer=request.user,
                rating=serializer.validated_data["rating"],
                comment=serializer.validated_data["comment"],
            )
            return Response(
                {
                    "message": "Review berhasil dibuat",
                    "review": {
                        "id": review.id,
                        "rating": review.rating,
                        "comment": review.comment,
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class ProductReviewListAPIView(APIView):
    def get(self, request, product_id):
        try:
            Product.objects.get(
                id=product_id
            )
        except Product.DoesNotExist:
            return Response(
                {
                    "message": "Produk tidak ditemukan"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        reviews = Review.objects.filter(
            product_id=product_id
        ).select_related(
            "buyer"
        )
        serializer = ReviewSerializer(
            reviews,
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
