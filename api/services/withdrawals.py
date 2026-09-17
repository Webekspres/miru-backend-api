"""Business rules for saldo withdrawal requests."""

from decimal import Decimal

from rest_framework.exceptions import ValidationError

from api.exceptions import AlreadyProcessedError
from api.models import PenarikanSaldo, User

MIN_NOMINAL = Decimal('50000')

# Penarikan besar: ≥ Rp1.000.000 wajib lampiran KTP
BESAR_NOMINAL = Decimal('1000000')

ALLOWED_METODE = frozenset({'tunai', 'transfer'})


def validate_nominal(nominal: Decimal) -> Decimal:
    """Raise list/str detail — aman dipanggil dari validate_nominal serializer."""
    if nominal < MIN_NOMINAL:
        raise ValidationError(
            f'Nominal penarikan minimal Rp{MIN_NOMINAL:,.0f}.'.replace(',', '.')
        )
    return nominal


def validate_metode(metode: str) -> str:
    """Raise list/str detail — aman dipanggil dari validate_metode serializer."""
    metode_norm = (metode or '').strip().lower()
    if metode_norm not in ALLOWED_METODE:
        raise ValidationError(
            'Metode penarikan tidak valid. Gunakan: tunai atau transfer.'
        )
    return metode_norm


def validate_saldo_cukup(nasabah: User, nominal: Decimal) -> None:
    nasabah.refresh_from_db()
    if nasabah.saldo < nominal:
        raise ValidationError({
            'nominal': [
                f'Saldo tidak mencukupi. Tersedia: Rp{nasabah.saldo}, '
                f'diminta: Rp{nominal}.'
            ],
        })


def validate_no_pending_withdrawal(nasabah: User, exclude_pk: int | None = None) -> None:
    qs = PenarikanSaldo.objects.filter(nasabah=nasabah, status='menunggu')
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise ValidationError({
            'nominal': [
                'Masih ada penarikan saldo yang menunggu persetujuan.',
            ],
        })


def is_besar(nominal: Decimal) -> bool:
    """Penarikan besar jika nominal ≥ Rp1.000.000."""
    return nominal >= BESAR_NOMINAL


def validate_create_withdrawal(
    nasabah: User,
    nominal: Decimal,
    metode: str | None = None,
) -> None:
    validate_nominal(nominal)
    if metode is not None:
        validate_metode(metode)
    validate_saldo_cukup(nasabah, nominal)
    validate_no_pending_withdrawal(nasabah)


def validate_approve_withdrawal(instance: PenarikanSaldo) -> None:
    validate_saldo_cukup(instance.nasabah, instance.nominal)


def _ensure_pending(instance: PenarikanSaldo) -> None:
    if instance.status != 'menunggu':
        raise AlreadyProcessedError('Penarikan saldo sudah diproses.')


def approve_withdrawal(instance: PenarikanSaldo) -> PenarikanSaldo:
    _ensure_pending(instance)
    validate_approve_withdrawal(instance)
    instance.status = 'selesai'
    purge_lampiran_ktp(instance)
    instance.save(update_fields=['status', 'lampiran_ktp', 'ktp_diverifikasi'])
    return instance


def reject_withdrawal(instance: PenarikanSaldo) -> PenarikanSaldo:
    """Tolak pengajuan — saldo tidak pernah didebit saat create, jadi tidak perlu refund."""
    _ensure_pending(instance)
    instance.status = 'ditolak'
    purge_lampiran_ktp(instance)
    instance.save(update_fields=['status', 'lampiran_ktp', 'ktp_diverifikasi'])
    return instance


def purge_lampiran_ktp(instance: PenarikanSaldo) -> None:
    """Hapus file KTP setelah tujuan verifikasi selesai. Jangan simpan di profil."""
    had_file = bool(instance.lampiran_ktp)
    if instance.lampiran_ktp:
        try:
            instance.lampiran_ktp.delete(save=False)
        except OSError:
            name = instance.lampiran_ktp.name
            if name:
                try:
                    instance.lampiran_ktp.storage.delete(name)
                except OSError:
                    pass
    instance.lampiran_ktp = None
    if had_file:
        instance.ktp_diverifikasi = True
