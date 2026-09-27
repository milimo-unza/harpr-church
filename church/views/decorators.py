from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """Allow only active Programme Coordinators."""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        membership = (
            request.user.church_memberships.filter(
                role="admin",
                is_active=True,
            )
            .select_related("church")
            .first()
        )
        if not membership:
            raise PermissionDenied("Programme Coordinator access required.")
        request.church = membership.church
        return view_func(request, *args, **kwargs)

    return wrapper


def dept_head_required(view_func):
    """Allow only active Department Heads."""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        membership = (
            request.user.church_memberships.filter(
                role="dept_head",
                is_active=True,
            )
            .select_related("church", "department")
            .first()
        )
        if not membership:
            raise PermissionDenied("Department Head access required.")
        request.church = membership.church
        request.department = membership.department
        return view_func(request, *args, **kwargs)

    return wrapper