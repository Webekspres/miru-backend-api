from rest_framework import permissions


class IsAdminOrKoordinator(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ['admin', 'koordinator']
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsPetugasOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ['petugas', 'admin']
        )


class IsNasabah(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'nasabah'
        )


class IsPickupManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'petugas')
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'koordinator', 'petugas']:
            return True
        return hasattr(obj, 'nasabah') and obj.nasabah == request.user


class IsUserOwnerOrAdmin(permissions.BasePermission):
    """Object-level permission for the User model (/api/users/{id}/)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role == 'koordinator':
            return view.action in ('retrieve', 'destroy')
        if user.role == 'nasabah':
            return (
                obj.pk == user.pk
                and view.action in ('retrieve', 'update', 'partial_update')
            )
        return False
