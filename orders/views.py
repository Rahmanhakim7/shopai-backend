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
from django.shortcuts import get_object_or_404
from payments.models import Payment
import uuid;

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
        Payment.objects.create(
            order=order,
            transaction_id=str(uuid.uuid4()),
            amount=total_amount,
            status=Payment.Status.PENDING,
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
            for item in items:
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

class CancelOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsBuyer,
    ]
    @transaction.atomic
    def post(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            buyer=request.user,
        )
        payment = getattr(order, "payment", None)
        if payment is None:
            return Response(
                {
                    "detail": "Data pembayaran tidak ditemukan."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        if payment.status != Payment.Status.PENDING:
            return Response(
                {
                    "detail": (
                        "Hanya pesanan yang menunggu pembayaran "
                        "yang dapat dibatalkan."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if order.seller_orders.exclude(status="pending").exists():
            return Response(
                {
                    "detail": "Pesanan tidak dapat dibatalkan karena sudah diproses."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment.status = Payment.Status.CANCELLED
        payment.save(
            update_fields=[
                "status",
            ]
        )
        order.seller_orders.update(
            status="cancelled"
        )
        return Response(
            {
                "message": "Pesanan berhasil dibatalkan.",
                "payment_status": payment.status,
            },
            status=status.HTTP_200_OK,
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

class ProcessSellerOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]
    @transaction.atomic
    def post(self, request, pk):
        seller_order = get_object_or_404(
            SellerOrder.objects.select_related("order", "order__payment"),
            pk=pk,
            seller=request.user,
        )
        payment = seller_order.order.payment
        if payment.status != Payment.Status.PAID:
            return Response(
                {
                    "detail": "Pesanan belum dibayar."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if seller_order.status != "pending":
            return Response(
                {
                    "detail": "Pesanan sudah diproses."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        seller_order.status = "processed"
        seller_order.save(
            update_fields=[
                "status",
            ]
        )
        return Response(
            {
                "message": "Pesanan berhasil diproses.",
                "status": seller_order.status,
            },
            status=status.HTTP_200_OK,
        )

class ShipSellerOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsSeller,
    ]
    @transaction.atomic
    def post(self, request, pk):
        seller_order = get_object_or_404(
            SellerOrder.objects.select_related(
                "order",
                "order__payment",
            ),
            pk=pk,
            seller=request.user,
        )
        payment = seller_order.order.payment
        if payment.status != Payment.Status.PAID:
            return Response(
                {
                    "detail": "Pesanan belum dibayar."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if seller_order.status != "processed":
            return Response(
                {
                    "detail": "Pesanan belum diproses."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        seller_order.status = "shipped"
        seller_order.save(
            update_fields=[
                "status",
            ]
        )
        return Response(
            {
                "message": "Pesanan berhasil dikirim.",
                "status": seller_order.status,
            },
            status=status.HTTP_200_OK,
        )

class CompleteSellerOrderAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsBuyer,
    ]
    @transaction.atomic
    def post(self, request, pk):
        seller_order = get_object_or_404(
            SellerOrder.objects.select_related(
                "order",
                "order__buyer",
                "order__payment",
            ),
            pk=pk,
        )
        if seller_order.order.buyer != request.user:
            return Response(
                {
                    "detail": "Anda tidak memiliki akses ke pesanan ini."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        payment = seller_order.order.payment
        if payment.status != Payment.Status.PAID:
            return Response(
                {
                    "detail": "Pesanan belum dibayar."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if seller_order.status != "shipped":
            return Response(
                {
                    "detail": "Pesanan belum dikirim."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        seller_order.status = "completed"
        seller_order.save(
            update_fields=[
                "status",
            ]
        )
        return Response(
            {
                "message": "Pesanan berhasil diselesaikan.",
                "status": seller_order.status,
            },
            status=status.HTTP_200_OK,
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