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


class IsStaffManagerOrPetugas(permissions.BasePermission):
    """Admin, koordinator, atau petugas — untuk lookup nasabah."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'koordinator', 'petugas')
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
        user = request.user
        if user.role == 'pemerintah':
            return request.method in permissions.SAFE_METHODS
        if user.role in ['admin', 'koordinator', 'petugas']:
            return True
        return hasattr(obj, 'nasabah') and obj.nasabah == user


class IsPemerintahReadOnly(permissions.BasePermission):
    """Pemerintah distrik: hanya boleh akses read (GET/HEAD/OPTIONS)."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'pemerintah':
            return request.method in permissions.SAFE_METHODS
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'pemerintah':
            return request.method in permissions.SAFE_METHODS
        return True


class IsMonitorReadOnly(permissions.BasePermission):
    """Admin, koordinator, pemerintah — akses read untuk monitoring."""

    def has_permission(self, request, view):
        from api.querysets import READ_ALL_ROLES
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in READ_ALL_ROLES
        )


class IsDashboardOverviewReader(permissions.BasePermission):
    """Admin/koordinator/pemerintah (full) atau petugas (widget sendiri)."""

    def has_permission(self, request, view):
        from api.querysets import READ_ALL_ROLES
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (*READ_ALL_ROLES, 'petugas')
        )


class IsActivityReader(permissions.BasePermission):
    """Nasabah (milik sendiri) atau staff read-all untuk riwayat gabungan."""

    def has_permission(self, request, view):
        from api.querysets import READ_ALL_ROLES
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('nasabah', *READ_ALL_ROLES)
        )


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
        if user.role == 'petugas':
            return (
                view.action == 'retrieve'
                and obj.role == 'nasabah'
                and request.method in permissions.SAFE_METHODS
            )
        if user.role == 'nasabah':
            return (
                obj.pk == user.pk
                and view.action in ('retrieve', 'update', 'partial_update')
            )
        return False
