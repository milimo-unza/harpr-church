"""Context available to every template."""


def harpr_context(request):
    """Expose the current membership role so templates can show the right nav."""
    role = None
    church = None
    if request.user.is_authenticated:
        membership = (
            request.user.church_memberships.filter(is_active=True)
            .select_related("church", "department")
            .first()
        )
        if membership:
            role = membership.role
            church = membership.church
    return {
        "app_name": "Harpr",
        "current_role": role,
        "current_church": church,
        "is_coordinator": role == "admin",
        "is_dept_head": role == "dept_head",
    }