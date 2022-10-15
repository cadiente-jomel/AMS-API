from django.urls import path

from .api.viewsets import (
    BranchAPIView,
    RetrieveBranchAPIView,
    TenantRoomAPIView,
    RetrieveTenantRoomAPIView,
    RoomAPIView,
    BranchRoomAPIView,
    RetrieveRoomAPIView,
)

app_name = "buildings"

urlpatterns = [
    path("branches", BranchAPIView.as_view(), name="branch"),
    path("branches/<int:pk>", RetrieveBranchAPIView.as_view(), name="branch-detail"),
    path("tenant-room/branch/<int:pk>", TenantRoomAPIView.as_view(), name="tenantroom"),
    path(
        "tenant-room/<int:pk>",
        RetrieveTenantRoomAPIView.as_view(),
        name="tenantroom-detail",
    ),
    path("rooms/branch/<int:pk>", BranchRoomAPIView.as_view(), name="room-branch"),
    path("rooms/", RoomAPIView.as_view(), name="room"),
    path("rooms/<int:pk>", RetrieveRoomAPIView.as_view(), name="room-detail"),
]
