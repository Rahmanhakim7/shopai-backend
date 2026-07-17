from orders.models import Order
from .models import Notification

def create_notification(
    *,
    user,
    notification_type: str,
    title: str,
    message: str,
    order: Order | None = None,
    seller_order=None,
) -> Notification:
    """
    Membuat satu notifikasi.
    """
    return Notification.objects.create(
        user=user,
        order=order,
        seller_order=seller_order,
        notification_type=notification_type,
        title=title,
        message=message,
    )

def notify_new_order(seller_order):
    return create_notification(
        user=seller_order.seller,
        order=seller_order.order,
        seller_order=seller_order,
        notification_type=Notification.NotificationType.NEW_ORDER,
        title="Pesanan Baru",
        message=f"Anda menerima pesanan baru #{seller_order.order.id}.",
    )

def notify_payment_success(seller_order) -> Notification:
    """
    Notifikasi ke seller ketika pembayaran berhasil.
    """
    return create_notification(
        user=seller_order.seller,
        order=seller_order.order,
        seller_order=seller_order,
        notification_type=Notification.NotificationType.PAYMENT_SUCCESS,
        title="Pembayaran Berhasil",
        message=f"Pembayaran untuk pesanan #{seller_order.order.id} telah diterima. Silakan proses pesanan.",
    )


def notify_order_processed(seller_order) -> Notification:
    """
    Notifikasi ke buyer ketika seller memproses pesanan.
    """
    return create_notification(
        user=seller_order.order.buyer,
        order=seller_order.order,
        notification_type=Notification.NotificationType.ORDER_PROCESSED,
        title="Pesanan Diproses",
        message=(
            f"Pesanan #{seller_order.order.id} "
            "sedang diproses oleh seller."
        )
    )


def notify_order_shipped(seller_order) -> Notification:
    """
    Notifikasi ke buyer ketika seller mengirim pesanan.
    """
    return create_notification(
        user=seller_order.order.buyer,
        order=seller_order.order,   
        notification_type=Notification.NotificationType.ORDER_SHIPPED,
        title="Pesanan Dikirim",
        message=f"Pesanan #{seller_order.order.id} telah dikirim.",
    )


def notify_order_completed(seller_order) -> Notification:
    """
    Notifikasi ke seller ketika buyer mengonfirmasi pesanan diterima.
    """
    return create_notification(
        user=seller_order.seller,
        order=seller_order.order,
        seller_order=seller_order,
        notification_type=Notification.NotificationType.ORDER_COMPLETED,
        title="Pesanan Selesai",
        message=(
            f"Buyer telah mengonfirmasi "
            f"penerimaan pesanan #{seller_order.order.id}."
        ),
)


def notify_order_cancelled(
    *,
    order: Order,
    seller_order,
    recipient,
    cancelled_by: str,
) -> Notification:
    """
    Notifikasi pembatalan pesanan.
    recipient = buyer atau seller.
    cancelled_by = "buyer" atau "seller"
    """
    if cancelled_by == "buyer":
        message = f"Buyer membatalkan pesanan #{order.id}."
    else:
        message = f"Penjual membatalkan pesanan #{order.id}."
    return create_notification(
        user=recipient,
        order=order,
        seller_order=seller_order,
        notification_type=Notification.NotificationType.ORDER_CANCELLED,
        title="Pesanan Dibatalkan",
        message=message,
    )