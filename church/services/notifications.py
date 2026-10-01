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

def log_action(church, user, action, details="", reason="", service=None, service_item=None):
    """Write a ServiceLog entry. Centralised so every view logs consistently."""
    from church.models import ServiceLog
    if church is None:
        return None
    return ServiceLog.objects.create(
        church=church,
        user=user,
        action=action,
        details=details or "",
        reason=reason or "",
        service=service,
        service_item=service_item,
    )
