"""Business rules for reward point redemptions."""

from rest_framework.exceptions import ValidationError

from api.models import Reward, User


def validate_poin_cukup(nasabah: User, reward: Reward) -> None:
    nasabah.refresh_from_db()
    if nasabah.poin < reward.poin_dibutuhkan:
        raise ValidationError(
            f'Poin tidak mencukupi. Tersedia: {nasabah.poin}, '
            f'dibutuhkan: {reward.poin_dibutuhkan}.'
        )


def validate_reward_stok(reward: Reward) -> None:
    reward.refresh_from_db()
    if reward.stok <= 0:
        raise ValidationError('Stok reward habis.')


def validate_create_redemption(nasabah: User, reward: Reward) -> None:
    validate_poin_cukup(nasabah, reward)
    validate_reward_stok(reward)


def validate_approve_redemption(nasabah: User, reward: Reward) -> None:
    validate_create_redemption(nasabah, reward)
