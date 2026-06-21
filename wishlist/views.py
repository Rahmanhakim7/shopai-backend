from django.shortcuts import get_object_or_404
from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import Response
from products.models import Product
from .models import Wishlist
from .serializers import (
    WishlistSerializer,
    AddWishlistSerializer,
)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_wishlist(request):
    wishlists = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        "product",
        "product__seller"
    )
    serializer = WishlistSerializer(
        wishlists,
        many=True
    )
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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