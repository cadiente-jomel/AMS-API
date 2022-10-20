from django.urls import path

from .api.viewsets import (
    TransactionAPIView, 
    RetrieveTransactionAPIView, 
    PaymentAPIView, 
    RetrievePaymentAPIView,
)

app_name = "payments"

urlpatterns = [
    path("transactions", TransactionAPIView.as_view(), name="transaction"),
    path("transactions/<int:pk>", RetrieveTransactionAPIView.as_view(), name="transaction-detail"),
    path("payments", PaymentAPIView.as_view(), name="payment"),
    path("payments/<int:pk>", RetrievePaymentAPIView.as_view(), name="payment-detail"),
]
