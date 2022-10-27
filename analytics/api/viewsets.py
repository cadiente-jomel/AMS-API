import logging
from collections import OrderedDict
from django.db.models import Sum, Count, When, Case
from rest_framework import mixins, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from analytics.utils import aggregate_ticket_count, annotate_ticket_count
from .serializers import (
    AnalyticsPaymentsSerializer,
    AnalyticsBranchSerializer,
    AnalyticsTransactionSerializer,
)
from payments.models import Payment, Transaction
from buildings.models import Branch
from core.permissions import IsLandlordAuthenticated

logger = logging.getLogger("secondary")
analytics_parameter = openapi.Parameter(
    "branch_id",
    openapi.IN_QUERY,
    description="ID of the specific branch",
    type=openapi.TYPE_STRING,
)


class AnalyticsPaymentAPIView(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = AnalyticsPaymentsSerializer
    permission_classes = [
        IsLandlordAuthenticated,
    ]

    user_response = openapi.Response(
        "Payment analytics for specific branches By default, without the parameter, it aggregates all the payments of all the branches the landlord assigned to combine.",
        AnalyticsPaymentsSerializer,
    )

    @swagger_auto_schema(
        manual_parameters=[analytics_parameter], responses={200: user_response}
    )
    def get(self, request, *args, **kwargs):
        queryset = Payment.objects.filter(
            tenant__room__branch__assigned_landlord=request.user
        )

        branch_id = request.query_params.get("branch_id", None)
        if branch_id is not None and branch_id != "''" and branch_id != '""':
            queryset = queryset.filter(tenant__room__branch__id=branch_id)

        rent_payments = queryset.filter(type="R")
        misc_payments = queryset.filter(type="Misc")

        data = dict()
        data["count"] = queryset.count()
        data["count_due_date"] = queryset.filter(due_date__isnull=False).count()
        data["count_wo_due_date"] = queryset.filter(due_date__isnull=True).count()
        data["total_payments"] = queryset.aggregate(total_payments=Sum("amount"))[
            "total_payments"
        ]
        data["total_rent_payments"] = rent_payments.aggregate(
            total_payments=Sum("amount")
        )["total_payments"]
        data["total_misc_payments"] = misc_payments.aggregate(
            total_payments=Sum("amount")
        )["total_payments"]

        serializer = self.serializer_class(data)
        return Response(serializer.data)


class AnalyticsBranchAPIView(generics.GenericAPIView):
    """By Default it counts the total tickets for all the branches combined
    specify a parameter 'branch_id' to see the ticket count for a specific branch"""

    serializer_class = AnalyticsBranchSerializer
    permission_classes = [
        IsLandlordAuthenticated,
    ]

    user_response = openapi.Response(
        "By default, it counts the total number of tickets to all the branches the landlord has assigned to. Specify the parameter to count it per branch.",
        AnalyticsBranchSerializer,
    )

    @swagger_auto_schema(
        manual_parameters=[analytics_parameter], responses={200: user_response}
    )
    def get(self, request, *args, **kwargs):
        queryset = Branch.objects.filter(assigned_landlord=request.user)
        data = dict()

        branch_id = request.query_params.get("branch_id", None)

        # simply this later just use Q models instead of aggregating or annotating
        if branch_id is not None and branch_id != "''" and branch_id != '""':
            data["count_tickets"] = annotate_ticket_count(queryset, branch_id)
            data["count_answered"] = annotate_ticket_count(queryset, branch_id, True)
            data["count_unanswered"] = annotate_ticket_count(queryset, branch_id, False)
            serializer = self.serializer_class(data)
            return Response(serializer.data)

        data["count_tickets"] = aggregate_ticket_count(queryset)
        data["count_answered"] = aggregate_ticket_count(queryset, True)
        data["count_unanswered"] = aggregate_ticket_count(queryset, False)

        serializer = self.serializer_class(data)
        return Response(serializer.data)


class AnalyticsTransactionSerializer(generics.GenericAPIView):
    serializer_class = AnalyticsTransactionSerializer
    permission_classes = [
        IsLandlordAuthenticated,
    ]
    user_response = openapi.Response(
        "By default, it counts the total number of transactions to all the branches the landlord has assigned to. Specify the parameter to count it per branch.",
        AnalyticsTransactionSerializer,
    )

    @swagger_auto_schema(
        manual_parameters=[analytics_parameter], responses={200: user_response}
    )
    def get(self, request, *args, **kwargs):
        queryset = Transaction.objects.filter(
            payment__tenant__room__branch__assigned_landlord=request.user
        )
        branch_id = request.query_params.get("branch_id", None)

        if branch_id is not None and branch_id != "''" and branch_id != '""':
            queryset = queryset.filter(payment__tenant__room__branch__id=branch_id)

        data = {"count_transaction": queryset.count()}

        serializer = self.serializer_class(data)
        return Response(serializer.data)
