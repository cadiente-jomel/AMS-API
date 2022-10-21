import logging
from collections import OrderedDict
from django.db.models import Sum
from rest_framework import (
    generics,
    mixins,
    status
)
from rest_framework.response import Response
from .serializers import PaymentSerializer, TransactionSerializer
from payments.utils import calculate_payments
from payments.models import Payment, Transaction
from core.permissions import (IsLandlordAuthenticated, IsUserAuthenticated)
from core.mixins import DestroyInstanceMixin

logger = logging.getLogger("secondary")

class PaymentAPIView(
    generics.GenericAPIView, 
    mixins.ListModelMixin
):
    serializer_class = PaymentSerializer
    permission_classes = [IsLandlordAuthenticated, ]
    
    def get_queryset(self):
        queryset = Payment.objects.select_related(
            "tenant"
        ).filter(tenant__room__branch__assigned_landlord=self.request.user)

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, 
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data["tenant"]
        if not validated_data.room.branch.assigned_landlord == request.user:
            return Response(
                {"detail": "You don't have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def perform_create(self, serializer) -> None:
        serializer.save()



class RetrievePaymentAPIView(
    generics.GenericAPIView, 
    mixins.RetrieveModelMixin,
    DestroyInstanceMixin,
):
    serializer_class = PaymentSerializer
    permission_classes = [IsUserAuthenticated, ]

    def get_queryset(self):
        queryset = Payment.objects.select_related(
            "tenant"
        ).filter(tenant__room__branch__assigned_landlord=self.request.user)

        return queryset

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            instance=self.get_object(),
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data["tenant"]
        if not validated_data.room.branch.assigned_landlord == request.user:
            return Response(
                {"detail": "You don't have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def delete(self, request, *args, **kwargs):
        if request.user.role != "LL":
            return Response({"detail": "You don't have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)
        return self.destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()

class TransactionAPIView(
    generics.GenericAPIView,
    mixins.ListModelMixin
):
    serializer_class = TransactionSerializer
    permission_classes = [IsUserAuthenticated, ]
    
    def get_queryset(self):
        user = self.request.user
        queryset = None
        if user.role == "T":
            queryset = Transaction.objects.select_related(
                "payment"
            ).filter(payment__tenant__tenant=user)
            return queryset

        queryset = Transaction.objects.select_related(
            "payment"
        ).filter(payment__tenant__room__branch__assigned_landlord=self.request.user)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True, context={"request": request})
         
        calculated_payments = calculate_payments(request, queryset, Payment)
        return Response(OrderedDict([
            ("overall_total", calculated_payments["overall_total"]),
            ("total_payment", calculated_payments["total_payment"]),
            ("remaining_balance", calculated_payments["remaining_balance"]),
            ("result", serializer.data)
        ]))

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, 
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data["payment"]
        if not validated_data.tenant.room.branch.assigned_landlord == request.user:
            return Response(
                {"detail": "You don't have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer) -> None:
        serializer.save()


class RetrieveTransactionAPIView(
    generics.GenericAPIView,
    mixins.RetrieveModelMixin,
    DestroyInstanceMixin
):
    queryset = Transaction.objects.select_related("payment").all()
    serializer_class = TransactionSerializer
    permission_classes = [IsUserAuthenticated, ]
    
    def get_queryset(self):
        user = self.request.user
        queryset = None
        if user.role == "T":
            queryset = Transaction.objects.select_related(
                "payment"
            ).filter(payment__tenant__tenant=user)
            return queryset

        queryset = Transaction.objects.select_related(
            "payment"
        ).filter(payment__tenant__room__branch__assigned_landlord=self.request.user)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(
            self.get_object(),
            context={"request": request}
        )

        calculated_payments = calculate_payments(request, queryset, Payment)
        return Response(OrderedDict([
            ("overall_total", calculated_payments["overall_total"]),
            ("total_payment", calculated_payments["total_payment"]),
            ("remaining_balance", calculated_payments["remaining_balance"]),
            ("result", serializer.data)
        ]))

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            instance=self.get_object(),
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data["payment"]
        if not validated_data.tenant.room.branch.assigned_landlord == request.user:
            return Response(
                {"detail": "You don't have permission to perform this action"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_update(self, serializer) -> None:
        serializer.save()

