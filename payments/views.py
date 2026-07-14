from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from orders.models import Order
from shopai.permissions import IsBuyer
from .serializers import (
    CreatePaymentSerializer,
    PaymentSerializer,
)
from .services import (
    create_snap_transaction, 
    update_payment_status, 
    verify_signature
)

class CreatePaymentAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsBuyer,
    ]

    @transaction.atomic
    def post(self, request):
        serializer = CreatePaymentSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        order_id = serializer.validated_data[
            "order_id"
        ]
        try:
            order = (
                Order.objects
                .select_related(
                    "buyer",
                    "payment",
                )
                .prefetch_related(
                    "seller_orders",
                    "seller_orders__items",
                    "seller_orders__items__product",
                )
                .get(
                    id=order_id,
                    buyer=request.user,
                )
            )
        except Order.DoesNotExist:
            return Response(
                {
                    "detail": "Pesanan tidak ditemukan."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        payment = order.payment
        # Jika Snap Token sudah pernah dibuat,
        # langsung gunakan yang lama.
        if payment.snap_token:
            return Response(
                PaymentSerializer(payment).data
            )
        # Buat transaksi ke Midtrans
        payment = create_snap_transaction(
            order,
            payment,
        )
        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )
    
class PaymentNotificationAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        order_id = request.data.get(
            "order_id"
        )
        status_code = request.data.get(
            "status_code"
        )
        gross_amount = request.data.get(
            "gross_amount"
        )
        signature_key = request.data.get(
            "signature_key"
        )
        transaction_status = request.data.get(
            "transaction_status"
        )
        transaction_id = request.data.get(
            "order_id"
        )

        if not verify_signature(
            order_id,
            status_code,
            gross_amount,
            signature_key,
        ):
            return Response(
                {
                    "detail": "Signature tidak valid."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        payment = update_payment_status(
            transaction_id,
            transaction_status,
        )
        
        if payment is None:
            return Response(
                {
                    "detail": "Payment tidak ditemukan"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "message": "Status pembayaran diperbarui"
            }
        )
    

    