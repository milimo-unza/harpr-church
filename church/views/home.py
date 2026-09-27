"""Role-aware home."""
from django.shortcuts import redirect, render


def home(request):
    """Anonymous: public landing page. Signed-in staff: their dashboard."""
    if not request.user.is_authenticated:
        return render(request, "public/landing.html")
    membership = (
        request.user.church_memberships.filter(is_active=True)
        .values_list("role", flat=True)
        .first()
    )
    if membership == "admin":
        return redirect("admin_dashboard")
    if membership == "dept_head":
        return redirect("dept_dashboard")
    return render(request, "public/landing.html")
