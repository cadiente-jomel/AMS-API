from rest_framework import permissions
from buildings.models import TenantRoom, Room, Branch


class IsLandlordAuthenticated(permissions.BasePermission):
    """Check if the current logged in user is landlord."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):

        if isinstance(obj, TenantRoom):
            return obj.room.branch.assigned_landlord == request.user

        if isinstance(obj, Room):
            return obj.branch.assigned_landlord == request.user
        
        if isinstance(obj, Branch):
            return obj.assigned_landlord == request.user

class IsTenantAuthenticated(permissions.BasePermission):
    """Check if the current logged in user is tenant."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.tenant == request.user
