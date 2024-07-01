from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class IsAdminOrDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        if request.user.profile.role == 'D' or request.user.is_superuser:
            return True
        return False