from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from church.models import Bulletin, Service, ServiceItem, ServiceLog


@transaction.atomic
def recalculate_times(service, anchor_item, new_actual_start, user=None, reason=""):
    """
    Apply the anchor item's delay to later, unlocked, incomplete service items.

    Returns the anchor and all subsequent items whose actual start was updated.
    """
    if anchor_item.service_id != service.pk:
        raise ValueError("The anchor item must belong to the supplied service.")

    offset = new_actual_start - anchor_item.planned_start
    changed = []

    anchor_item.actual_start = new_actual_start
    anchor_item.status = "changed"
    anchor_item.save(update_fields=["actual_start", "status", "updated_at"])
    changed.append(anchor_item)

    subsequent = service.items.filter(order__gt=anchor_item.order).order_by("order")
    for item in subsequent:
        if item.lock_actual_start or item.status == "completed":
            continue
        item.actual_start = item.planned_start + offset
        item.save(update_fields=["actual_start", "updated_at"])
        changed.append(item)

    ServiceLog.objects.create(
        church=service.church,
        user=user,
        service=service,
        service_item=anchor_item,
        action="time_shifted",
        details=f"Shifted {len(changed)} items by {offset}",
        reason=reason,
    )
    return changed


@transaction.atomic
def freeze_service(service, user, reason=""):
    """Create a versioned bulletin snapshot and mark the service frozen."""
    locked_service = Service.objects.select_for_update().select_related("church").get(
        pk=service.pk
    )
    if locked_service.status == "frozen":
        return locked_service.bulletins.order_by("-version").first()

    snapshot = {
        "service": {
            "name": locked_service.name,
            "date": locked_service.date.isoformat(),
            "church": locked_service.church.name,
        },
        "items": [
            {
                "order": item.order,
                "title": item.title,
                "planned_start": item.planned_start.isoformat(),
                "duration_minutes": item.planned_duration_minutes,
                "department": (
                    item.responsible_department.name
                    if item.responsible_department
                    else None
                ),
                "assignments": [
                    {"name": assignment.person_name, "role": assignment.role}
                    for assignment in item.assignments.all()
                ],
                "notes": item.notes,
            }
            for item in locked_service.items.select_related(
                "responsible_department"
            ).prefetch_related("assignments").order_by("order")
        ],
    }

    latest = locked_service.bulletins.order_by("-version").first()
    version = latest.version + 1 if latest else 1
    bulletin = Bulletin.objects.create(
        service=locked_service,
        version=version,
        snapshot_json=snapshot,
        frozen_by=user,
    )

    locked_service.status = "frozen"
    locked_service.frozen_at = timezone.now()
    locked_service.frozen_by = user
    locked_service.save(update_fields=["status", "frozen_at", "frozen_by", "updated_at"])

    ServiceLog.objects.create(
        church=locked_service.church,
        user=user,
        service=locked_service,
        action="frozen",
        details=f"Bulletin v{version} frozen",
        reason=reason,
    )
    return bulletin


@transaction.atomic
def unfreeze_service(service, user, reason):
    """Return a service to draft status; a reason is required and audited."""
    if not reason or not reason.strip():
        raise ValueError("A reason is required to unfreeze a service.")

    locked_service = Service.objects.select_for_update().select_related("church").get(
        pk=service.pk
    )
    locked_service.status = "draft"
    locked_service.frozen_at = None
    locked_service.frozen_by = None
    locked_service.unfrozen_reason = reason.strip()
    locked_service.save(
        update_fields=[
            "status",
            "frozen_at",
            "frozen_by",
            "unfrozen_reason",
            "updated_at",
        ]
    )

    ServiceLog.objects.create(
        church=locked_service.church,
        user=user,
        service=locked_service,
        action="unfrozen",
        details="Bulletin unfrozen",
        reason=reason.strip(),
    )