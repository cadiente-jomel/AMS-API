from django.db import transaction 
from rest_framework import (
    generics,    
    mixins,
    status,
)
from rest_framework.response import Response

from core.permissions import (
    IsLandlordAuthenticated, 
    IsUserAuthenticated,
)
from core.mixins import DestroyInstanceMixin 
from emergency_contacts.models import EmergencyContact
from .serializers import EmergencyContactSerializer


class EmergencyContactsAPIView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
): 
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsUserAuthenticated, ]
    
    def get_queryset(self):
        branch = self.request.query_params.get("branch", None)
        user = self.request.user
        if user.role == "T":
            queryset = EmergencyContact.objects.select_related(
                "branch"
            ).filter(branch__branch_room__tenantroom__tenant=user)
            return queryset

        queryset = EmergencyContact.objects.select_related(
            "branch"
        ).filter(branch__assigned_landlord=user)

        if branch is not None:
            queryset = queryset.filter(branch_id=branch)

        return queryset
        

    def get(self, request, *args, **kwargs):
        if request.user.role == "NA":
            return Response(
                {"detail": "You don't have permission to perform this action."},                
                status=status.HTTP_403_FORBIDDEN
            )
        return self.list(request, *args, **kwargs)
    
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data["branch"]
        if not validated_data.assigned_landlord == request.user:
            return Response(
                {"detail": "You don't have permission to perform this action."},                
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer) -> None:
        serializer.save()


class RetrieveEmergencyContactsAPIView(
    generics.GenericAPIView, 
    mixins.RetrieveModelMixin,
    DestroyInstanceMixin,
):
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsUserAuthenticated]

    def get_queryset(self):
        queryset = EmergencyContact.objects.all()
        return queryset

    @transaction.atomic()
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            instance=self.get_object(),
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data["branch"]
        if not validated_data.assigned_landlord == request.user:
            return Response(
                {"detail": "You don't have permission to perform this action."},                
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_update(self, serializer) -> None:
        serializer.save()
