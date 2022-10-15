import logging
from django.db import transaction
from rest_framework import status, generics, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import RoomSerializer, BranchSerializer, TenantRoomSerializer

from core.permissions import IsLandlordAuthenticated
from core.mixins import DestroyInstanceMixin
from buildings.models import (
    Branch,
    Room,
    TenantRoom,
)
from users.models import Landlord, Tenant

logger = logging.getLogger('secondary')

class BranchAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = BranchSerializer
    permission_classes = [IsLandlordAuthenticated, ]

    def get_queryset(self):
        tenant = self.request.user
        branches = Branch.objects.select_related("assigned_landlord").filter(
            assigned_landlord=tenant
        )
        return branches

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Exception as err:
            return Response({"error": "Something went wrong while performing this action."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def perform_create(self, serializer) -> None:
        serializer.save()


class RetrieveBranchAPIView(
    mixins.RetrieveModelMixin, 
    mixins.DestroyModelMixin, 
    generics.GenericAPIView
):
    serializer_class = BranchSerializer
    permission_classes = [IsLandlordAuthenticated, ]

    def get_queryset(self):
        user = self.request.user
        branch = Branch.objects.select_related("assigned_landlord").filter(
            assigned_landlord=user
        )

        return branch

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *aargs, **kwargs):
        serializer = self.serializer_class(
            data=request.data, 
            instance=self.get_object, 
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data["assigned_landlord"]
        if not validated_data == request.user:
            return Response(
                {"detail": "You don't have permission to perform this action."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer) -> None:
        serializer.save()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class RoomAPIView(generics.GenericAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsLandlordAuthenticated, ]
    
    def get_queryset(self):
        user = self.request.user
        objs = Room.objects.select_related(
            "branch"
        ).filter(branch__assigned_landlord=user)

        return objs

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = RoomSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class BranchRoomAPIView(generics.GenericAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsLandlordAuthenticated, ]

    def get_queryset(self):
        branch = self.kwargs.get("pk", None)
        # if branch is not None:
        #     user =
        rooms = Room.objects.select_related("branch").filter(branch=branch)

        return rooms

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "No rooms for this branch or branch simply doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Exception as err:
            return Response({"error": "Something went wrong while performing this action."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveRoomAPIView(
    mixins.RetrieveModelMixin, 
    mixins.DestroyModelMixin, 
    generics.GenericAPIView
):
    queryset = Room.objects.select_related("branch").all()
    serializer_class = RoomSerializer
    permission_classes = [IsLandlordAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

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

    def perform_update(self, serializer) -> None:
        serializer.save()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TenantRoomAPIView(generics.GenericAPIView):
    serializer_class = TenantRoomSerializer
    permission_classes = [IsLandlordAuthenticated, ]

    def get_queryset(self):
        branch = self.kwargs["pk"]

        qs = TenantRoom.objects.select_related("room", "tenant").filter(
            room__branch__id=branch
        )

        room_no = self.request.query_params.get("room", None)
        if room_no is None or room_no == "''" or room_no == '""':
            return qs

        qs = qs.filter(room__pk=room_no)

        return qs

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Exception as err:
            return Response({"error": "Something went wrong while performing this action."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

    def get(self, request, *args, **kwargs):
        user_id = TenantRoom.objects.filter(
            room__branch__id=kwargs["pk"]
        ).first().room.branch.assigned_landlord.pk
        
        # TODO  make this if block a decorator if it becomes repetitive.
        if not request.user.id == user_id:
            return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "No existing record."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer) -> None:
        serializer.save()


class RetrieveTenantRoomAPIView(
    DestroyInstanceMixin, 
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    queryset = TenantRoom.objects.all()
    serializer_class = TenantRoomSerializer
    permission_classes = [IsLandlordAuthenticated, ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    @transaction.atomic()
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @transaction.atomic()
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, 
            instance=self.get_object(), 
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data["room"]
        if not validated_data.branch.assigned_landlord == request.user:
            return Response(
                {"detail": "You don't have permission to perform this action."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_update(serializer)  
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer) -> None:
        serializer.save()

