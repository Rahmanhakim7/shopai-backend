from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from .models import (
    Order,
    SellerOrder,
    OrderItem,
)
from .serializers import (
    CreateOrderSerializer,
    OrderSerializer,
    SellerOrderSerializer
)
from shopai.permissions import IsBuyer,IsSeller

class CreateOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsBuyer
    ]
    @transaction.atomic
    def post(self, request):
        serializer = CreateOrderSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        items_data = (
            serializer
            .validated_data["items"]
        )
        checkout_items = []
        for item_data in items_data:
            try:
                product = (
                    Product.objects
                    .select_related(
                        "seller"
                    )
                    .select_for_update()
                    .get(
                        id=item_data["product_id"]
                    )
                )
            except Product.DoesNotExist:
                return Response(
                    {
                        "detail":
                        f"Produk {item_data['product_id']} tidak ditemukan"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            quantity = item_data["quantity"]
            checkout_items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "price": product.price
                }
            )

        for item in checkout_items:
            if item["quantity"] > item["product"].stock:
                return Response(
                    {
                        "detail":
                        f"Stok {item['product'].name} tidak mencukupi"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        total_amount = sum(
            item["quantity"] *
            item["price"]
            for item in checkout_items
        )
        order = Order.objects.create(
            buyer=request.user,
            total_amount=total_amount
        )
        seller_groups = {}
        for item in checkout_items:
            seller_id = (
                item["product"].seller_id
            )
            if seller_id not in seller_groups:
                seller_groups[seller_id] = []
            seller_groups[seller_id].append(
                item
            )
        for seller_id, items in seller_groups.items():
            seller_total = sum(
                item["quantity"] *
                item["price"]
                for item in items
            )
            seller_order = SellerOrder.objects.create(
                order=order,
                seller=items[0]["product"].seller,
                subtotal=seller_total
            )
            order_items = []
            for item in checkout_items:
                subtotal = (
                    item["quantity"] *
                    item["price"]
                )
                order_items.append(
                    OrderItem(
                        seller_order=seller_order,
                        product=item["product"],
                        quantity=item["quantity"],
                        price=item["price"],
                        subtotal=subtotal
                    )
                )
            OrderItem.objects.bulk_create(
                order_items
            )
        for item in checkout_items:
            product = item["product"]
            product.stock -= item["quantity"]

            if product.stock <= 0:
                product.stock = 0
                product.status = "sold_out"

            product.save(
                update_fields=[
                    "stock",
                    "status"
                ]
            )
        return Response(
            {
                "message":
                "Order berhasil dibuat",
                "order_id":
                order.id,
                "total_amount":
                order.total_amount,
            },
            status=status.HTTP_201_CREATED
        )
class BuyerOrderListAPIView(
    ListAPIView
):
    serializer_class = OrderSerializer
    permission_classes = [
        IsAuthenticated,
        IsBuyer
    ]

    def get_queryset(self):
        return (
            Order.objects
            .filter(
                buyer=self.request.user
            )
            .prefetch_related(
                "seller_orders",
                "seller_orders__seller",
                "seller_orders__items",
                "seller_orders__items__product",
            )
            .order_by(
                "-created_at"
            )
        )
    
class BuyerOrderDetailAPIView(
    RetrieveAPIView
):
    serializer_class = OrderSerializer
    permission_classes = [
        IsAuthenticated,
        IsBuyer
    ]
    def get_queryset(self):
        return (
            Order.objects
            .filter(
                buyer=self.request.user

            )
            .prefetch_related(
                "seller_orders",
                "seller_orders__seller",
                "seller_orders__items",
                "seller_orders__items__product",
            )
        )

class SellerOrderListAPIView(
    ListAPIView
):
    serializer_class = SellerOrderSerializer
    permission_classes = [
        IsAuthenticated,
        IsSeller
    ]

    def get_queryset(self):
        return (
            SellerOrder.objects
            .filter(
                seller=self.request.user
            )
            .select_related(
                "order",
                "order__buyer",
                "seller",
            )
            .prefetch_related(
                "items",
                "items__product",
            )
            .order_by("-created_at")
        )

class SellerOrderDetailAPIView(
    RetrieveAPIView
):
    serializer_class = SellerOrderSerializer
    permission_classes = [
        IsAuthenticated,
        IsSeller
    ]

    def get_queryset(self):
        return (
            SellerOrder.objects
            .filter(
                seller=self.request.user
            )
            .select_related(
                "order",
                "order__buyer",
                "seller",
            )
            .prefetch_related(
                "items",
                "items__product",
            )
        )

class UpdateSellerOrderStatusAPIView(
    APIView
):
    permission_classes = [
        IsAuthenticated,
        IsSeller    
    ]

    def patch(self, request, pk):
        try:
            seller_order = (
                SellerOrder.objects.get(
                    pk=pk,
                    seller=request.user
                )
            )
        except SellerOrder.DoesNotExist:
            return Response(
                {
                    "detail":
                    "Pesanan tidak ditemukan"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get(
            "status"
        )

        valid_statuses = [
            "pending",
            "processed",
            "shipped",
            "completed",
        ]

        if new_status not in valid_statuses:
            return Response(
                {
                    "detail":
                    "Status tidak valid"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        seller_order.status = new_status
        seller_order.save()

        return Response(
            {
                "message":
                "Status berhasil diperbarui",
                "status":
                seller_order.status,
            }
        )