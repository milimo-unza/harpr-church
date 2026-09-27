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