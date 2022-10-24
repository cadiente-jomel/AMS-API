from django.urls import path
from .api.viewsets import AnalyticsPaymentAPIView

app_name = "analytics"

urlpatterns = [ 
    path("", AnalyticsPaymentAPIView.as_view(), name="payment-analytics")
]
