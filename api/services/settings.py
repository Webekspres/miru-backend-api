"""Institution settings singleton helpers."""

from api.models import PengaturanInstitusi


def get_institution_settings() -> PengaturanInstitusi:
    """Return the singleton institution settings row (creates defaults if missing)."""
    return PengaturanInstitusi.load()
