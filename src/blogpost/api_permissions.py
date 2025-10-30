from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Custom permission: allow safe methods for anyone, write only for author or staff."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only to author or staff
        return getattr(request.user, 'is_staff', False) or getattr(obj, 'author', None) == request.user
