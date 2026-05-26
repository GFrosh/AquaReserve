from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Reservation can be viewed/modified by its owner or by admins."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        is_admin = getattr(request.user, 'is_admin_role', False) or request.user.is_staff
        return is_admin or obj.user_id == request.user.id


class IsAdminUserRole(permissions.BasePermission):
    """Allow only users with admin role / staff."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'is_admin_role', False) or request.user.is_staff
