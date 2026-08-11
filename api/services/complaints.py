"""Business rules for nasabah complaints."""

from rest_framework.exceptions import ValidationError

VALID_JENIS = {
    'saldo_belum_masuk',
    'penjemputan_terlambat',
    'berat_tidak_sesuai',
    'harga_tidak_sesuai',
    'petugas_tidak_datang',
    'kesalahan_data',
    'bukti_tidak_muncul',
    'lainnya',
}


def validate_jenis_pengaduan(jenis: str) -> str:
    if jenis not in VALID_JENIS:
        raise ValidationError('Jenis pengaduan tidak valid.')
    return jenis


def validate_admin_close(tindak_lanjut: str, status: str) -> None:
    if status == 'ditutup' and not (tindak_lanjut or '').strip():
        raise ValidationError(
            {'tindak_lanjut': ['Tindak lanjut wajib diisi saat menutup pengaduan.']}
        )
