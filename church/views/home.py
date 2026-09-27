"""Role-aware home redirect so each user lands on the right dashboard."""

from django.shortcuts import redirect


def home(request):
    """Send anonymous users to login, coordinators to the dashboard,
    department heads to their department view."""
    if not request.user.is_authenticated:
        return redirect("login")
    membership = (
        request.user.church_memberships.filter(is_active=True)
        .values_list("role", flat=True)
        .first()
    )
    if membership == "admin":
        return redirect("admin_dashboard")
    if membership == "dept_head":
        return redirect("dept_dashboard")
    return redirect("login")