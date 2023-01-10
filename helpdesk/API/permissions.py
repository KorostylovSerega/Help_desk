from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsUserOrAdminReadOnly(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and not request.user.is_staff or
                    request.user.is_authenticated and request.method in SAFE_METHODS)
