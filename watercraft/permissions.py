from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Read for everyone, write for admins only."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'is_admin_role', False) or request.user.is_staff
