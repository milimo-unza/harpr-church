from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from church.models import Notification


def _user_notifications(user):
    church_ids = user.church_memberships.filter(is_active=True).values_list(
        "church_id", flat=True
    )
    return Notification.objects.filter(user=user, church_id__in=church_ids)


@login_required
def api_notifications(request):
    notifications = _user_notifications(request.user)
    unread = notifications.filter(is_read=False)
    data = [
        {
            "id": notification.pk,
            "title": notification.title,
            "body": notification.body,
            "url": notification.url,
            "created_at": notification.created_at.isoformat(),
        }
        for notification in unread[:20]
    ]
    return JsonResponse({"notifications": data, "unread_count": unread.count()})


@login_required
@require_POST
def api_notification_read(request, pk):
    notification = get_object_or_404(_user_notifications(request.user), pk=pk)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return JsonResponse({"ok": True})


@login_required
@require_POST
def api_notifications_mark_all_read(request):
    updated = _user_notifications(request.user).filter(is_read=False).update(is_read=True)
    return JsonResponse({"ok": True, "updated": updated})

@login_required
def api_activity(request):
    """Return recent ServiceLog entries visible to this user.

    Coordinators see the full church log. Department heads see nothing here
    (their activity feed lives in the notification bell)."""
    membership = (
        request.user.church_memberships.filter(is_active=True)
        .select_related("church")
        .first()
    )
    if not membership:
        return JsonResponse({"entries": [], "scope": "none"})

    if membership.role != "admin":
        return JsonResponse({"entries": [], "scope": "dept_head"})

    logs = (
        membership.church.logs
        .select_related("user", "service")
        .order_by("-created_at")[:10]
    )
    entries = []
    for entry in logs:
        meta_bits = [entry.created_at.strftime("%d %b %H:%M")]
        if entry.user:
            meta_bits.append(entry.user.username)
        if entry.service:
            meta_bits.append(entry.service.name)
        detail = entry.details or entry.reason or "—"
        entries.append({
            "action": entry.get_action_display(),
            "detail": detail,
            "meta": " · ".join(meta_bits),
            "url": "/dashboard/",
        })
    return JsonResponse({"entries": entries})
