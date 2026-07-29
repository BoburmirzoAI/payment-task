from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only users with role='admin' can access."""
    message = "PERMISSION_DENIED"

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsRegularUser(BasePermission):
    """Only users with role='user' can access."""
    message = "PERMISSION_DENIED"

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "user"
        )


class IsAdminOrOwner(BasePermission):
    """Admin can access any object. User can only access their own."""
    message = "PERMISSION_DENIED"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        # obj must have user_id or user field
        owner_id = getattr(obj, "user_id", None) or getattr(getattr(obj, "user", None), "id", None)
        return str(owner_id) == str(request.user.id)
