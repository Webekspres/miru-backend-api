"""Signal handlers for automatic AuditLog recording.

Uses pre_save to capture old state and post_save to compare and log.
For deletes, post_delete creates a delete audit entry.
"""

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from api.middleware import get_client_ip, get_current_request, get_current_user
from api.models import (
    AuditLog,
    KategoriSampah,
    Pengaduan,
    PenarikanSaldo,
    Penjemputan,
    PenukaranPoin,
    TransaksiSetoran,
    User,
)

# Fields to exclude from audit changes (noisy/internal)
EXCLUDED_FIELDS = {
    'last_login',
    'password',
    'updated_at',
    'lampiran_ktp',
}
# Fields to include only for certain models
USER_EXCLUDED = EXCLUDED_FIELDS | {'date_joined'}


def _get_changed_fields(instance, old_instance=None) -> dict:
    """Compare instance with its old state and return {field: (old, new)}.

    Only returns fields that actually changed.
    """
    changed = {}
    excluded = USER_EXCLUDED if isinstance(instance, User) else EXCLUDED_FIELDS
    if old_instance is None:
        # New instance — capture all non-excluded fields as created
        for field in instance._meta.fields:
            name = field.name
            if name in excluded or name.endswith('ptr'):
                continue
            new_val = _serialize_value(getattr(instance, name))
            if _is_significant(new_val):
                changed[name] = {'old': None, 'new': new_val}
    else:
        for field in instance._meta.fields:
            name = field.name
            if name in excluded or name.endswith('ptr'):
                continue
            old_val = _serialize_value(getattr(old_instance, name))
            new_val = _serialize_value(getattr(instance, name))
            if old_val != new_val:
                changed[name] = {'old': old_val, 'new': new_val}
    return changed


def _serialize_value(value):
    """Convert field values to JSON-serializable types."""
    if value is None:
        return None
    if hasattr(value, 'pk'):
        return value.pk
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def _is_significant(value):
    """Check if a value is significant enough to log."""
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str) and value.strip() == '':
        return False
    return True


def _create_audit_entry(
    instance,
    action: str,
    changes: dict | None = None,
):
    """Create an AuditLog entry from the current request context."""
    user = get_current_user()
    request = get_current_request()

    ip_address = None
    if request:
        ip_address = get_client_ip(request)

    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        model_name=instance._meta.model.__name__,
        object_id=str(instance.pk),
        changes=changes or {},
        ip_address=ip_address,
    )


# ──────────────────────────────────────────────
# Internal state holders for pre_save tracking
# ──────────────────────────────────────────────

def _capture_pre_save(instance):
    """Store field values from DB before save (instance may already be mutated in memory)."""
    values = {}
    if instance.pk:
        old = instance.__class__.objects.filter(pk=instance.pk).first()
        if old is not None:
            excluded = USER_EXCLUDED if isinstance(old, User) else EXCLUDED_FIELDS
            for field in old._meta.fields:
                name = field.name
                if name in excluded or name.endswith('ptr'):
                    continue
                values[name] = _serialize_value(getattr(old, name))
            instance._audit_pre_save_state = values
            return
    for field in instance._meta.fields:
        name = field.name
        if name in EXCLUDED_FIELDS or name.endswith('ptr'):
            continue
        values[name] = _serialize_value(getattr(instance, name))
    instance._audit_pre_save_state = values


def _get_pre_save_state(instance):
    """Retrieve and clear the pre-save state for an instance."""
    values = getattr(instance, '_audit_pre_save_state', None)
    if values is not None:
        del instance._audit_pre_save_state
    return values


# ──────────────────────────────────────────────
# Universal pre_save — capture old state
# ──────────────────────────────────────────────


@receiver(pre_save, sender=User)
@receiver(pre_save, sender=TransaksiSetoran)
@receiver(pre_save, sender=PenarikanSaldo)
@receiver(pre_save, sender=Penjemputan)
@receiver(pre_save, sender=PenukaranPoin)
@receiver(pre_save, sender=KategoriSampah)
@receiver(pre_save, sender=Pengaduan)
def audit_pre_save(sender, instance, **kwargs):
    """Capture the old state before save."""
    if instance.pk is None:
        return  # New instance — no old state needed
    _capture_pre_save(instance)
    # Save old status for notification signal handlers (not all models have 'status')
    old = instance.__class__.objects.filter(pk=instance.pk).first()
    if old is not None:
        instance._old_status = getattr(old, 'status', None)


# ──────────────────────────────────────────────
# Universal post_save — log create / update
# ──────────────────────────────────────────────


@receiver(post_save, sender=User)
@receiver(post_save, sender=TransaksiSetoran)
@receiver(post_save, sender=PenarikanSaldo)
@receiver(post_save, sender=KategoriSampah)
@receiver(post_save, sender=Pengaduan)
def audit_post_save(sender, instance, created, **kwargs):
    """Log create or update to AuditLog."""
    if created:
        changes = _get_changed_fields(instance)
        if changes:
            _create_audit_entry(instance, 'create', changes)
    else:
        old_state = _get_pre_save_state(instance)
        if old_state:
            changes = {}
            for field in instance._meta.fields:
                name = field.name
                if name in (USER_EXCLUDED if isinstance(instance, User) else EXCLUDED_FIELDS) or name.endswith('ptr'):
                    continue
                old_val = old_state.get(name)
                new_val = _serialize_value(getattr(instance, name))
                if old_val != new_val:
                    changes[name] = {'old': old_val, 'new': new_val}
            if changes:
                _create_audit_entry(instance, 'update', changes)


# ──────────────────────────────────────────────
# Universal post_delete — log delete
# ──────────────────────────────────────────────


@receiver(post_delete, sender=User)
@receiver(post_delete, sender=TransaksiSetoran)
@receiver(post_delete, sender=PenarikanSaldo)
@receiver(post_delete, sender=KategoriSampah)
@receiver(post_delete, sender=Pengaduan)
def audit_post_delete(sender, instance, **kwargs):
    """Log delete to AuditLog with the last known values."""
    changes = {}
    for field in instance._meta.fields:
        name = field.name
        if name in EXCLUDED_FIELDS:
            continue
        val = _serialize_value(getattr(instance, name))
        if _is_significant(val):
            changes[name] = {'old': val, 'new': None}
    _create_audit_entry(instance, 'delete', changes)
