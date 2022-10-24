from collections import OrderedDict
from django.db.models import Sum
from rest_framework import (
    mixins,
    generics,
    status
)
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import (
    AnalyticsPaymentsSerializer,
    AnalyticsBranchSerializer,
    AnalyticsTransactionSerializer,
)
from payments.models import (
    Payment,
    Transaction
)
from buildings.models import Branch
from core.permissions import IsLandlordAuthenticated


class AnalyticsPaymentAPIView(
    generics.GenericAPIView, 
    mixins.ListModelMixin
):
    serializer_class = AnalyticsPaymentsSerializer
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        queryset = Payment.objects.filter(
            tenant__room__branch__assigned_landlord=request.user
        )

        rent_payments = queryset.filter(type="R")
        misc_payments = queryset.filter(type="Misc")
        
        data = dict()
        data["count"] = queryset.count()
        data["count_due_date"] = queryset.filter(due_date__isnull=False).count()
        data["count_wo_due_date"] = queryset.filter(due_date__isnull=True).count()
        data["total_payments"] = queryset.aggregate(total_payments=Sum("amount"))["total_payments"]
        data["total_rent_payments"] = rent_payments.aggregate(total_payments=Sum("amount"))["total_payments"] 
        data["total_misc_payments"] = misc_payments.aggregate(total_payments=Sum("amount"))["total_payments"]


        serializer = self.serializer_class(data)
        return Response(serializer.data)



        

