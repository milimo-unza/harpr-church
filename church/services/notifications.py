from church.models import Membership, Notification


def notify_user(user, title, body="", url="", church=None):
    if not user:
        return None
    try:
        if hasattr(user, "settings") and not user.settings.notifications_enabled:
            return None
    except Exception:
        pass
    return Notification.objects.create(
        user=user, church=church, title=title, body=body, url=url
    )


def notify_department(church, department, title, body="", url=""):
    if not department:
        return
    for membership in Membership.objects.filter(
        church=church,
        department=department,
        role="dept_head",
        is_active=True,
    ).select_related("user"):
        notify_user(membership.user, title, body, url, church=church)