from rest_framework import serializers
from buildings.models import Branch, Room, TenantRoom


class BranchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Branch
        fields = [
            "id",
            "url",
            "assigned_landlord",
            "location",
            "number_of_rooms",
            "building_type",
        ]
        extra_kwargs = {
            "url": {"view_name": "buildings:branch-detail"},
            "assigned_landlord": {"view_name": "users:landlord-detail"},
        }


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = [
            "id",
            "url",
            "branch",
            "room_no",
            "capacity",
            "type",
        ]
        extra_kwargs = {
            "url": {"view_name": "buildings:room-detail"},
            "branch": {"view_name": "buildings:branch-detail"},
        }


class TenantRoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TenantRoom
        fields = [
            "id",
            "url",
            "room",
            "tenant",
        ]
        extra_kwargs = {
            "url": {"view_name": "buildings:tenantroom-detail"},
            "room": {"view_name": "buildings:room-detail"},
            "tenant": {"view_name": "users:tenant-detail"},
        }
