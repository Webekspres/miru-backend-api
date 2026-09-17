from django.contrib import admin

from api.models import (
    KontenEdukasi, DeviceToken, Notifikasi, PasswordResetToken, PoinTransaksi,
    PengaturanInstitusi, Pengumuman, RiwayatHarga, WilayahLayanan,
)


@admin.register(PengaturanInstitusi)
class PengaturanInstitusiAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not PengaturanInstitusi.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pengumuman)
class PengumumanAdmin(admin.ModelAdmin):
    list_display = ('judul', 'aktif', 'tanggal')
    list_filter = ('aktif',)


@admin.register(RiwayatHarga)
class RiwayatHargaAdmin(admin.ModelAdmin):
    list_display = ('kategori', 'harga_lama', 'harga_baru', 'tanggal_berlaku', 'diubah_oleh')
    list_filter = ('kategori',)
    readonly_fields = ('kategori', 'harga_lama', 'harga_baru', 'tanggal_berlaku', 'diubah_oleh')


@admin.register(WilayahLayanan)
class WilayahLayananAdmin(admin.ModelAdmin):
    list_display = ('kelurahan', 'rt', 'rw', 'aktif', 'created_at')
    list_filter = ('aktif',)
    search_fields = ('kelurahan', 'rt', 'rw')
    list_editable = ('aktif',)
    ordering = ('kelurahan', 'rt', 'rw')


@admin.register(KontenEdukasi)
class KontenEdukasiAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori_terkait', 'aktif', 'created_at')
    list_filter = ('aktif', 'kategori_terkait')
    search_fields = ('judul', 'isi')
    list_editable = ('aktif',)
    ordering = ('-created_at',)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_short', 'created_at', 'is_used', 'is_expired')
    list_filter = ('is_used',)
    search_fields = ('user__username', 'token')
    readonly_fields = ('user', 'token', 'created_at', 'is_used')
    date_hierarchy = 'created_at'

    def token_short(self, obj):
        return f'{obj.token[:16]}…'
    token_short.short_description = 'Token'

    def has_add_permission(self, request):
        return False  # Token dibuat otomatis oleh sistem

    def has_change_permission(self, request, obj=None):
        return False  # Token tidak bisa diubah manual


@admin.register(PoinTransaksi)
class PoinTransaksiAdmin(admin.ModelAdmin):
    list_display = ('user', 'jumlah', 'sisa', 'sumber', 'tanggal_dibuat', 'tanggal_kedaluwarsa', 'is_expired')
    list_filter = ('sumber', 'is_expired')
    search_fields = ('user__username', 'user__nama_lengkap')
    readonly_fields = ('user', 'jumlah', 'sisa', 'sumber', 'setoran', 'tanggal_dibuat', 'tanggal_kedaluwarsa', 'is_expired')
    date_hierarchy = 'tanggal_kedaluwarsa'

    def has_add_permission(self, request):
        return False  # PoinTransaksi dibuat otomatis oleh sistem

    def has_change_permission(self, request, obj=None):
        return False  # PoinTransaksi tidak bisa diubah manual


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'token_short', 'updated_at')
    list_filter = ('platform',)
    search_fields = ('user__username', 'token')
    readonly_fields = ('user', 'token', 'platform', 'created_at', 'updated_at')

    def token_short(self, obj):
        return f'{obj.token[:16]}…'
    token_short.short_description = 'Token'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Notifikasi)
class NotifikasiAdmin(admin.ModelAdmin):
    list_display = ('judul', 'user', 'kategori', 'is_read', 'created_at')
    list_filter = ('kategori', 'is_read', 'created_at')
    search_fields = ('judul', 'deskripsi', 'user__username', 'user__nama_lengkap')
    readonly_fields = ('user', 'judul', 'deskripsi', 'kategori', 'is_read', 'created_at')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False  # Notifikasi dibuat otomatis oleh sistem

    def has_change_permission(self, request, obj=None):
        return False  # Notifikasi tidak bisa diubah manual
