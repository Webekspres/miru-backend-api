"""Business rules for reward point redemptions.

Qty default = 1 per baris penukaran (multi-qty belum masuk kontrak API).
Biaya poin di-snapshot saat create; approve memakai snapshot.
"""

from rest_framework.exceptions import ValidationError

from api.exceptions import AlreadyProcessedError
from api.models import PenukaranPoin, Reward, User

# Satu pengajuan = satu unit reward sampai multi-qty disepakati.
DEFAULT_REDEMPTION_QTY = 1


def validate_poin_cukup(nasabah: User, poin_dibutuhkan: int) -> None:
    nasabah.refresh_from_db()
    if nasabah.poin < poin_dibutuhkan:
        raise ValidationError({
            'reward': [
                f'Poin tidak mencukupi. Tersedia: {nasabah.poin}, '
                f'dibutuhkan: {poin_dibutuhkan}.'
            ],
        })


def validate_reward_stok(reward: Reward, qty: int = DEFAULT_REDEMPTION_QTY) -> None:
    reward.refresh_from_db()
    if reward.stok < qty:
        raise ValidationError({'reward': ['Stok reward habis.']})


def validate_create_redemption(nasabah: User, reward: Reward) -> None:
    validate_poin_cukup(nasabah, reward.poin_dibutuhkan)
    validate_reward_stok(reward)


def validate_approve_redemption(instance: PenukaranPoin) -> None:
    """Approve memakai snapshot poin_dibutuhkan, bukan harga katalog terbaru."""
    validate_poin_cukup(instance.nasabah, instance.poin_dibutuhkan)
    validate_reward_stok(instance.reward)


def _ensure_pending(instance: PenukaranPoin) -> None:
    if instance.status != 'menunggu':
        raise AlreadyProcessedError('Penukaran poin sudah diproses.')


def approve_redemption(instance: PenukaranPoin) -> PenukaranPoin:
    _ensure_pending(instance)
    validate_approve_redemption(instance)
    instance.status = 'selesai'
    instance.save(update_fields=['status'])
    return instance


def reject_redemption(instance: PenukaranPoin) -> PenukaranPoin:
    """Admin menolak pengajuan — poin tidak pernah didebit saat create."""
    _ensure_pending(instance)
    instance.status = 'ditolak'
    instance.save(update_fields=['status'])
    return instance


def cancel_redemption(instance: PenukaranPoin) -> PenukaranPoin:
    """Nasabah membatalkan pengajuan yang masih menunggu."""
    _ensure_pending(instance)
    instance.status = 'dibatalkan'
    instance.save(update_fields=['status'])
    return instance
