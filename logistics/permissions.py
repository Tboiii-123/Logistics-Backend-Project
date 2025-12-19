# permissions.py
from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "admin"
        )


class IsDriverUser(BasePermission):
    """
    Allows access only to authenticated users who are drivers.
    """

    def has_permission(self, request, view):
        # Make sure user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Option 1: Using role attribute on user
        if hasattr(request.user, 'role') and request.user.role == "driver":
            return True
       
        return False
