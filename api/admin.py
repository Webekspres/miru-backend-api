from django.contrib import admin

from api.models import Notifikasi, PengaturanInstitusi, Pengumuman, RiwayatHarga


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
