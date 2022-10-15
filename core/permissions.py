from rest_framework import permissions
from buildings.models import TenantRoom, Room, Branch


class IsLandlordAuthenticated(permissions.BasePermission):
    """Check if the current logged in user is landlord."""
    def has_permission(self, request, view) -> bool:
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == "LL"
        )

    def has_object_permission(self, request, view, obj) -> bool:

        if isinstance(obj, TenantRoom):
            return bool(obj.room.branch.assigned_landlord == request.user)

        if isinstance(obj, Room):
            return bool(obj.branch.assigned_landlord == request.user)
        
        if isinstance(obj, Branch):
            return bool(obj.assigned_landlord == request.user)

class IsTenantAuthenticated(permissions.BasePermission):
    """Check if the current logged in user is tenant."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user and 
            request.user.is_authenticated and
            request.user.role == "T"
        )

    def has_object_permission(self, request, view, obj) -> bool:
        return bool(obj.tenant == request.user)


class IsUserAuthenticated(permissions.BasePermission):
    """Check if a user is logged in regardless of role"""
    def has_permission(self, request, view) -> bool:
        return bool(
            request.user and 
            request.user.is_authenticated
        )

    def has_object_parmission(self, request, view, obj) -> bool:
        return bool(obj.answered_by == request.user)

