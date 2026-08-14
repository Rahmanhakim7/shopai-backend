from django.shortcuts import get_object_or_404
from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import Response
from core.pagination import WishlistPagination
from products.models import Product
from .models import Wishlist
from .serializers import (
    WishlistSerializer,
    AddWishlistSerializer,
)
from shopai.permissions import IsBuyer

class WishlistListView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated, IsBuyer]
    pagination_class = WishlistPagination

    def get_queryset(self):
        return (
            Wishlist.objects.filter(user=self.request.user)
            .select_related(
                "product",
                "product__seller",
            )
            .order_by("-id")
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsBuyer])
def add_to_wishlist(request):
    serializer = AddWishlistSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product = get_object_or_404(
        Product,
        id=serializer.validated_data["product_id"]
    )
    wishlist = Wishlist.objects.filter(
        user=request.user,
        product=product
    )
    if wishlist.exists():
        wishlist.delete()
        return Response(
            {"message": "Wishlist removed"}
        )
    Wishlist.objects.create(
        user=request.user,
        product=product
    )
    return Response(
        {"message": "Wishlist added"}
    )

@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsBuyer])
def remove_wishlist(
    request,
    product_id
):
    if request.user.role != "buyer":
        return Response(
            {
                "message":
                "Only buyers can remove wishlist"
            },
            status=403
        )
    wishlist = get_object_or_404(
        Wishlist,
        user=request.user,
        product_id=product_id
    )
    wishlist.delete()
    return Response({
        "message":
        "Wishlist removed"
    })