from django.urls import path
from .views import CreatePaymentAPIView, PaymentNotificationAPIView

urlpatterns = [
    path(
        "create/",
        CreatePaymentAPIView.as_view(),
        name="create-payment",
    ),
    path(
        "notification/",
        PaymentNotificationAPIView.as_view(),
    ),
]