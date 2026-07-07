from rest_framework import permissions

class IsAdminOrKoordinator(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['admin', 'koordinator'])

class IsPetugasOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['petugas', 'admin', 'koordinator'])

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'koordinator', 'petugas']:
            return True
        return hasattr(obj, 'nasabah') and obj.nasabah == request.user
