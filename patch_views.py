"""Standalone patch script for admin_views.py.
Replaces admin_dashboard with the Sunday-first version and adds two member guards. Run once from ~/harpr.
"""

from pathlib import Path

path = Path("church/views/admin_views.py")
text = path.read_text()

# --- Fix 1: replace admin_dashboard ---
start_marker = "@admin_required\ndef admin_dashboard(request):"
end_marker = "\n\n@admin_required\ndef service_list(request):"

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx == -1 or end_idx == -1:
    raise SystemExit("Could not locate admin_dashboard block. Aborting.")

new_dashboard = """@admin_required
def admin_dashboard(request):
    from datetime import date, timedelta

    today = timezone.localdate()
    week_param = request.GET.get("week")

    if week_param:
        try:
            ref = date.fromisoformat(week_param)
        except (ValueError, TypeError):
            ref = today
    else:
        ref = today

    # Sunday-first week: Sunday.weekday() == 6, so shift forward by 1
    days_since_sunday = (ref.weekday() + 1) % 7
    week_start = ref - timedelta(days=days_since_sunday)
    week_end = week_start + timedelta(days=6)

    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)

    services = request.church.services.filter(
        date__range=(week_start, week_end)
    ).prefetch_related("items")
    events = request.church.events.filter(
        date__range=(week_start, week_end)
    ).select_related("responsible_department")

    days = []
    for day_offset in range(7):
        day = week_start + timedelta(days=day_offset)
        days.append({
            "date": day,
            "services": [s for s in services if s.date == day],
            "events": [e for e in events if e.date == day],
        })

    return render(request, "church/dashboard.html", {
        "church": request.church,
        "today": today,
        "week_start": week_start,
        "week_end": week_end,
        "prev_week": prev_week,
        "next_week": next_week,
        "days": days,
        "service_count": request.church.services.filter(
            date__year=today.year, date__month=today.month
        ).count(),
        "pending_request_count": request.church.requests.filter(
            status="pending"
        ).count(),
        "recent_activity": request.church.logs.select_related(
            "user", "service", "service_item"
        )[:10],
        "service_templates": request.church.service_templates.filter(is_active=True),
        "departments": request.church.departments.all(),
    })"""

text = text[:start_idx] + new_dashboard + text[end_idx:]

# --- Fix 2: Guard 1 ---
old_guard_1 = (
    "def member_deactivate(request, pk):\n"
    "    membership = get_object_or_404(request.church.memberships, pk=pk)\n"
    "    membership.is_active = False"
)
new_guard_1 = (
    "def member_deactivate(request, pk):\n"
    "    membership = get_object_or_404(request.church.memberships, pk=pk)\n"
    "    if membership.user == request.user:\n"
    "        messages.error(request, \"You cannot deactivate your own account.\")\n"
    "        return redirect(\"member_list\")\n"
    "    membership.is_active = False"
)

if old_guard_1 not in text:
    raise SystemExit("Guard 1 target not found. Aborting.")
text = text.replace(old_guard_1, new_guard_1, 1)

# --- Fix 3: Guard 2 ---
old_guard_2 = (
    "    if request.method == \"POST\" and form.is_valid():\n"
    "        data = form.cleaned_data\n"
    "        membership.role = data[\"role\"]"
)
new_guard_2 = (
    "    if request.method == \"POST\" and form.is_valid():\n"
    "        data = form.cleaned_data\n"
    "        if membership.user == request.user and data[\"role\"] != \"admin\":\n"
    "            messages.error(request, \"You cannot change your own role from Administrator.\")\n"
    "            return redirect(\"member_list\")\n"
    "        membership.role = data[\"role\"]"
)

if old_guard_2 not in text:
    raise SystemExit("Guard 2 target not found. Aborting.")
text = text.replace(old_guard_2, new_guard_2, 1)

path.write_text(text)
print("All three patches applied to admin_views.py.")
