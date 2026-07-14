import uuid
import hashlib
import midtransclient
from django.conf import settings
from .models import Payment
from django.db import transaction

snap = midtransclient.Snap(
    is_production=settings.MIDTRANS_IS_PRODUCTION,
    server_key=settings.MIDTRANS_SERVER_KEY,
    client_key=settings.MIDTRANS_CLIENT_KEY,
)

def build_transaction_details(order, transaction_id):
    return {
        "order_id": transaction_id,
        "gross_amount": order.total_amount,
    }


def build_customer_details(order):
    return {
        "first_name": order.buyer.username,
        "email": order.buyer.email,
    }


def build_item_details(order):
    item_details = []
    for seller_order in order.seller_orders.all():
        for item in seller_order.items.all():
            item_details.append(
                {
                    "id": str(item.product.id),
                    "price": item.price,
                    "quantity": item.quantity,
                    "name": item.product.name,
                }
            )
    return item_details

def create_snap_transaction(order, payment):
    transaction_id = f"SHOPAI-{uuid.uuid4().hex[:12]}"
    parameter = {
        "transaction_details": build_transaction_details(
            order,
            transaction_id,
        ),
        "customer_details": build_customer_details(
            order,
        ),
        "item_details": build_item_details(
            order,
        ),
    }
    response = snap.create_transaction(parameter)
    payment.transaction_id = transaction_id
    payment.snap_token = response["token"]
    payment.payment_url = response["redirect_url"]
    payment.save(
        update_fields=[
            "transaction_id",
            "snap_token",
            "payment_url",
        ]
    )
    return payment

@transaction.atomic
def update_payment_status(transaction_id, transaction_status):
    try:
        payment = (
            Payment.objects
            .select_related("order")
            .prefetch_related(
                "order__seller_orders",
                "order__seller_orders__items",
                "order__seller_orders__items__product",
            )
            .get(transaction_id=transaction_id)
        )
    except Payment.DoesNotExist:
        return None
    order = payment.order
    if transaction_status == "settlement":
        if payment.status != Payment.Status.PAID:
            payment.status = Payment.Status.PAID
            for seller_order in order.seller_orders.all():
                for item in seller_order.items.all():
                    product = item.product
                    product.stock -= item.quantity
                    if product.stock <= 0:
                        product.stock = 0
                        product.status = "sold_out"
                    product.save(
                        update_fields=[
                            "stock",
                            "status",
                        ]
                    )
    elif transaction_status == "pending":
        payment.status = Payment.Status.PENDING
    elif transaction_status == "expire":
        payment.status = Payment.Status.EXPIRED
    elif transaction_status in [
        "cancel",
        "deny",
        "failure",
    ]:
        payment.status = Payment.Status.FAILED
    payment.save(update_fields=["status"])
    return payment

def verify_signature(
    order_id,
    status_code,
    gross_amount,
    signature_key,
):
    raw_signature = (
        order_id
        + status_code
        + gross_amount
        + settings.MIDTRANS_SERVER_KEY
    )
    generated_signature = hashlib.sha512(
        raw_signature.encode()
    ).hexdigest()
    return generated_signature == signature_key