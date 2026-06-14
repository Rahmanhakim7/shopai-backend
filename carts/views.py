from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import UpdateCartItemSerializer
from .models import Cart, CartItem
from products.models import Product

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    if request.user.role != "buyer":
        return Response({"message": "Only buyers can add to cart"}, status=403)
    product_id = request.data.get("product_id")
    if not product_id:
        return Response({"message": "product_id is required"}, status=400)
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if product.stock < 1:
        return Response(
            {"message": "Stock tidak tersedia"},
            status=400
        )
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            "price_at_added": product.price
        }
    )
    if not created:
        if item.quantity + 1 > product.stock:
            return Response({"message": "Stock tidak cukup"}, status=400)
        item.quantity += 1
        item.save()
    return Response({"message": "Product added to cart"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request):

    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        return Response({
            "seller_groups": [],
            "total_price": 0
        })

    items = cart.items.select_related("product", "product__seller")

    cart_data = {}
    total_price = 0

    for item in items:
        product = item.product
        seller = product.seller

        seller_id = seller.id

        if seller_id not in cart_data:
            cart_data[seller_id] = {
                "seller_id": seller.id,
                "seller_name": seller.username,
                "items": [],
                "seller_total": 0
            }

        subtotal = item.item_total()

        cart_data[seller_id]["items"].append({
            "cart_item_id": item.id,
            "product_id": product.id,
            "name": product.name,
            "price": item.price_at_added,
            "quantity": item.quantity,
            "image": product.image.url if product.image else None,
            "subtotal": subtotal
        })

        cart_data[seller_id]["seller_total"] += subtotal
        total_price += subtotal

    return Response({
        "seller_groups": list(cart_data.values()),
        "total_price": total_price
    })

@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def cart_item_detail(request, cart_item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        cart__user=request.user
    )

    if request.method == "PATCH":

        serializer = UpdateCartItemSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data["quantity"]

        if quantity > cart_item.product.stock:
            return Response(
                {"message": "Stock tidak cukup"},
                status=400
            )

        cart_item.quantity = quantity
        cart_item.save()

        return Response({
            "message": "Cart updated"
        })

    elif request.method == "DELETE":

        cart_item.delete()

        return Response({
            "message": "Item removed from cart"
        })