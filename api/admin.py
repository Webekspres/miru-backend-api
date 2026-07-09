from django.contrib import admin

from api.models import PengaturanInstitusi, Pengumuman, RiwayatHarga


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
