from django.urls import path
from .api.viewsets import (
    AnalyticsPaymentAPIView,
    AnalyticsBranchAPIView,
    AnalyticsTransactionSerializer,
)

app_name = "analytics"

urlpatterns = [
    path("", AnalyticsPaymentAPIView.as_view(), name="payment-analytics"),
    path("branch", AnalyticsBranchAPIView.as_view(), name="branch-analytics"),
    path(
        "transaction",
        AnalyticsTransactionSerializer.as_view(),
        name="transaction-analytics",
    ),
]
