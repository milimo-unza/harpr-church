import json
from datetime import date, timedelta

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from church.forms import AssignmentForm, RequestForm
from church.models import (
    Assignment,
    DepartmentMember,
    Service,
    ServiceItem,
)
from church.views.decorators import dept_head_required


def _is_ajax(request):
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.headers.get("Accept", "").startswith("application/json")
    )


def _week_bounds(ref=None):
    """Sunday-first week containing `ref` (defaults to today)."""
    today = timezone.localdate()
    ref = ref or today
    days_since_sunday = (ref.weekday() + 1) % 7
    week_start = ref - timedelta(days=days_since_sunday)
    week_end = week_start + timedelta(days=6)
    return today, week_start, week_end


@dept_head_required
def dept_dashboard(request):
    """Week grid + department's own upcoming items, all in one page."""
    if not request.department:
        return render(request, "church/dept_dashboard.html", {
            "items": [],
            "pending_items": [],
            "roster": [],
            "roster_json": "[]",
            "days": [],
            "week_start": timezone.localdate(),
            "week_end": timezone.localdate(),
            "prev_week": timezone.localdate(),
            "next_week": timezone.localdate(),
            "today": timezone.localdate(),
            "department": None,
        })

    today, week_start, week_end = _week_bounds()

    # Allow ?week=YYYY-MM-DD navigation, matching the coordinator dashboard.
    week_param = request.GET.get("week")
    if week_param:
        try:
            ref = date.fromisoformat(week_param)
            today, week_start, week_end = _week_bounds(ref)
        except (ValueError, TypeError):
            pass

    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)

    # All church services + events this week (read-only for dept heads).
    services = request.church.services.filter(
        date__range=(week_start, week_end)
    ).prefetch_related("items__assignments")
    events = request.church.events.filter(
        date__range=(week_start, week_end)
    ).select_related("responsible_department")

    dept_id = request.department.pk if request.department else None

    days = []
    for day_offset in range(7):
        day = week_start + timedelta(days=day_offset)
        # Flag services/events whose responsible department matches.
        day_services = []
        for s in services:
            if s.date != day:
                continue
            s.has_my_items = any(
                it.responsible_department_id == dept_id
                for it in s.items.all()
            ) if dept_id else False
            day_services.append(s)
        day_events = []
        for e in events:
            if e.date != day:
                continue
            e.is_mine = (e.responsible_department_id == dept_id) if dept_id else False
            day_events.append(e)
        days.append({
            "date": day,
            "services": day_services,
            "events": day_events,
        })

    # The department's own items — future and today, ordered by time.
    dept_items = (
        ServiceItem.objects.filter(
            church=request.church,
            responsible_department=request.department,
            planned_start__gte=timezone.now(),
        )
        .select_related("service")
        .prefetch_related("assignments")
        .order_by("planned_start")
    )

    # Annotate each item with the set of names already assigned so the
    # template can grey them out in the picker.
    for item in dept_items:
        item.assigned_names = {a.person_name for a in item.assignments.all()}

    pending_items = [item for item in dept_items if not item.assignments.exists()]
    roster = DepartmentMember.objects.filter(
        department=request.department
    ).order_by("name")

    roster_json = json.dumps([
        {"pk": m.pk, "name": m.name, "phone": m.phone}
        for m in roster
    ])

    return render(request, "church/dept_dashboard.html", {
        "items": dept_items,
        "pending_items": pending_items,
        "roster": roster,
        "roster_json": roster_json,
        "days": days,
        "week_start": week_start,
        "week_end": week_end,
        "prev_week": prev_week,
        "next_week": next_week,
        "today": today,
        "department": request.department,
    })


@dept_head_required
def dept_item_detail(request, pk):
    """Kept for direct URLs — now redirects to the dashboard."""
    item = get_object_or_404(
        ServiceItem,
        pk=pk,
        church=request.church,
        responsible_department=request.department,
    )
    return redirect(f"{request.path.rsplit('/', 2)[0]}/?focus={item.pk}")


@dept_head_required
@require_POST
def dept_assignment_create(request, pk):
    """Add an assignment from the modal. Also saves the name to the roster."""
    item = get_object_or_404(
        ServiceItem,
        pk=pk,
        church=request.church,
        responsible_department=request.department,
    )

    # Accept both a single name and a list of names.
    names = request.POST.getlist("person_name")
    # Free-text fallback.
    free_text = request.POST.get("free_text_name", "").strip()
    if free_text:
        names.append(free_text)
    # De-dupe, drop blanks.
    names = [n.strip() for n in names if n and n.strip()]
    # Preserve order but remove repeats.
    seen = set()
    names = [n for n in names if not (n in seen or seen.add(n))]

    role = request.POST.get("role", "").strip() or item.title
    save_to_roster = request.POST.get("save_to_roster") == "on"

    if not names:
        if _is_ajax(request):
            return JsonResponse(
                {"ok": False, "errors": {"person_name": ["Pick at least one person."]}},
                status=400,
            )
        messages.error(request, "Pick at least one person.")
        return redirect("dept_dashboard")

    created = []
    skipped = []
    for name in names:
        # Don't create a duplicate for the same person on the same item.
        if Assignment.objects.filter(service_item=item, person_name=name).exists():
            skipped.append(name)
            continue
        assignment = Assignment.objects.create(
            service_item=item,
            person_name=name,
            role=role,
        )
        created.append(assignment)
        if save_to_roster:
            DepartmentMember.objects.get_or_create(
                church=request.church,
                department=request.department,
                name=name,
            )

    summary = ", ".join(a.person_name for a in created)
    if _is_ajax(request):
        return JsonResponse({
            "ok": True,
            "assignment_ids": [a.pk for a in created],
            "message": f"Assigned: {summary}",
        })

    messages.success(request, f"Assigned: {summary}")
    return redirect("dept_dashboard")


@dept_head_required
@require_POST
def dept_assignment_delete(request, pk):
    """Remove an assignment from an item (does not touch the roster)."""
    assignment = get_object_or_404(
        Assignment,
        pk=pk,
        service_item__church=request.church,
        service_item__responsible_department=request.department,
    )
    assignment.delete()

    if _is_ajax(request):
        return JsonResponse({"ok": True, "message": "Assignment removed."})

    messages.success(request, "Assignment removed.")
    return redirect("dept_dashboard")


@dept_head_required
def dept_roster(request):
    """List + add + remove saved department members."""
    if not request.department:
        return redirect("dept_dashboard")

    if request.method == "POST":
        action = request.POST.get("action", "add")
        if action == "add":
            name = request.POST.get("name", "").strip()
            phone = request.POST.get("phone", "").strip()
            if name:
                DepartmentMember.objects.get_or_create(
                    church=request.church,
                    department=request.department,
                    name=name,
                    defaults={"phone": phone},
                )
                messages.success(request, f"{name} added to your team.")
            else:
                messages.error(request, "Enter a name.")
        elif action == "update":
            member_id = request.POST.get("member_id")
            phone = request.POST.get("phone", "").strip()
            member = DepartmentMember.objects.filter(
                pk=member_id,
                department=request.department,
            ).first()
            if member:
                member.phone = phone
                member.save(update_fields=["phone"])
                messages.success(request, f"{member.name} updated.")
        elif action == "remove":
            member_id = request.POST.get("member_id")
            DepartmentMember.objects.filter(
                pk=member_id,
                department=request.department,
            ).delete()
            messages.success(request, "Team member removed.")
        return redirect("dept_roster")

    roster = DepartmentMember.objects.filter(
        department=request.department
    ).order_by("name")
    return render(request, "church/dept_roster.html", {
        "roster": roster,
        "department": request.department,
    })


@dept_head_required
def dept_request_create(request):
    initial = {}
    about = request.GET.get("about", "").strip()
    if about:
        initial["title"] = about[:200]
    form = RequestForm(request.POST or None, church=request.church, initial=initial)
    if request.method == "POST" and form.is_valid():
        from datetime import time as _time
        church_request = form.save(commit=False)
        church_request.church = request.church
        church_request.submitted_by = request.user
        start_raw = request.POST.get("start_date", "").strip()
        end_raw = request.POST.get("end_date", "").strip()
        if start_raw:
            try:
                church_request.start_date = date.fromisoformat(start_raw)
            except ValueError:
                pass
        if church_request.type == "announcement":
            if end_raw:
                try:
                    church_request.end_date = date.fromisoformat(end_raw)
                except ValueError:
                    pass
        elif church_request.type == "schedule":
            start_t = request.POST.get("start_time", "").strip()
            end_t = request.POST.get("end_time", "").strip()
            if start_t:
                try:
                    church_request.requested_start_time = _time.fromisoformat(start_t)
                except ValueError:
                    pass
            if end_t:
                try:
                    church_request.requested_end_time = _time.fromisoformat(end_t)
                except ValueError:
                    pass
        church_request.save()
        messages.success(request, "Request submitted.")
        return redirect("dept_request_list")
    return render(request, "church/dept_request_form.html", {"form": form})


@dept_head_required
def dept_request_list(request):
    requests = request.church.requests.filter(submitted_by=request.user)
    return render(request, "church/dept_requests.html", {"requests": requests})


@dept_head_required
def dept_request_detail(request, pk):
    """JSON for the dept head's request modal."""
    church_request = get_object_or_404(
        request.church.requests, pk=pk, submitted_by=request.user
    )
    return JsonResponse({
        "id": church_request.pk,
        "title": church_request.title,
        "body": church_request.body,
        "type": church_request.type,
        "type_display": church_request.get_type_display(),
        "start_date": church_request.start_date.isoformat() if church_request.start_date else "",
        "end_date": church_request.end_date.isoformat() if church_request.end_date else "",
        "requested_start_time": church_request.requested_start_time.strftime("%H:%M") if church_request.requested_start_time else "",
        "requested_end_time": church_request.requested_end_time.strftime("%H:%M") if church_request.requested_end_time else "",
        "status": church_request.status,
        "status_display": church_request.get_status_display(),
        "admin_response": church_request.admin_response or "",
        "created_at": church_request.created_at.strftime("%d %b %Y %H:%M"),
        "is_pending": church_request.status == "pending",
    })


@dept_head_required
@require_POST
def dept_request_edit(request, pk):
    """Dept head edits a pending request. Blocked once approved/rejected."""
    church_request = get_object_or_404(
        request.church.requests, pk=pk, submitted_by=request.user
    )
    if church_request.status != "pending":
        if _is_ajax(request):
            return JsonResponse(
                {"ok": False, "errors": {"__all__": ["Only pending requests can be edited."]}},
                status=400,
            )
        messages.error(request, "Only pending requests can be edited.")
        return redirect("dept_request_list")

    form = RequestForm(request.POST or None, church=request.church, instance=church_request)
    if form.is_valid():
        from datetime import time as _time
        obj = form.save(commit=False)
        obj.church = request.church
        obj.submitted_by = request.user
        start_raw = request.POST.get("start_date", "").strip()
        end_raw = request.POST.get("end_date", "").strip()
        if start_raw:
            try:
                obj.start_date = date.fromisoformat(start_raw)
            except ValueError:
                obj.start_date = None
        else:
            obj.start_date = None
        if obj.type == "announcement":
            obj.requested_start_time = None
            obj.requested_end_time = None
            if end_raw:
                try:
                    obj.end_date = date.fromisoformat(end_raw)
                except ValueError:
                    obj.end_date = None
            else:
                obj.end_date = None
        elif obj.type == "schedule":
            obj.end_date = None
            start_t = request.POST.get("start_time", "").strip()
            end_t = request.POST.get("end_time", "").strip()
            try:
                obj.requested_start_time = _time.fromisoformat(start_t) if start_t else None
            except ValueError:
                obj.requested_start_time = None
            try:
                obj.requested_end_time = _time.fromisoformat(end_t) if end_t else None
            except ValueError:
                obj.requested_end_time = None
        obj.save()
        if _is_ajax(request):
            return JsonResponse({"ok": True, "message": "Request updated."})
        messages.success(request, "Request updated.")
        return redirect("dept_request_list")

    if _is_ajax(request):
        return JsonResponse({"ok": False, "errors": _form_errors_json(form)}, status=400)
    messages.error(request, "Could not update request.")
    return redirect("dept_request_list")


@dept_head_required
@require_POST
def dept_request_delete(request, pk):
    """Dept head withdraws a pending request. Blocked once approved/rejected."""
    church_request = get_object_or_404(
        request.church.requests, pk=pk, submitted_by=request.user
    )
    if church_request.status != "pending":
        if _is_ajax(request):
            return JsonResponse(
                {"ok": False, "errors": {"__all__": ["Only pending requests can be withdrawn."]}},
                status=400,
            )
        messages.error(request, "Only pending requests can be withdrawn.")
        return redirect("dept_request_list")

    church_request.delete()
    if _is_ajax(request):
        return JsonResponse({"ok": True, "message": "Request withdrawn."})
    messages.success(request, "Request withdrawn.")
    return redirect("dept_request_list")


def _form_errors_json(form):
    return {field: [str(e) for e in errs] for field, errs in form.errors.items()}

@dept_head_required
def dept_service_schedule(request, pk):
    """Return the full item list for a service, as JSON, for the week-grid popup."""
    service = get_object_or_404(
        Service,
        pk=pk,
        church=request.church,
    )
    dept_id = request.department.pk if request.department else None

    items = []
    for item in service.items.select_related("responsible_department").prefetch_related("assignments").order_by("order"):
        is_mine = (
            dept_id is not None
            and item.responsible_department_id == dept_id
        )
        items.append({
            "id": item.pk,
            "time": item.planned_start.strftime("%H:%M"),
            "title": item.title,
            "department": item.responsible_department.name if item.responsible_department else "—",
            "assigned": [a.person_name for a in item.assignments.all()],
            "is_mine": is_mine,
            "unassigned": not item.assignments.exists(),
        })

    return JsonResponse({
        "service": {
            "id": service.pk,
            "name": service.name,
            "date": service.date.strftime("%A, %d %B %Y"),
            "status": service.get_status_display(),
        },
        "items": items,
    })


@dept_head_required
def dept_event_detail(request, pk):
    """Return one event's details as JSON, for the week-grid popup."""
    from church.models import ChurchEvent

    event = get_object_or_404(
        ChurchEvent,
        pk=pk,
        church=request.church,
    )
    return JsonResponse({
        "event": {
            "id": event.pk,
            "title": event.title,
            "type": event.get_event_type_display(),
            "date": event.date.strftime("%A, %d %B %Y"),
            "start_time": event.start_time.strftime("%H:%M"),
            "end_time": event.end_time.strftime("%H:%M"),
            "location": event.location or "—",
            "department": event.responsible_department.name if event.responsible_department else "—",
            "notes": event.notes or "",
        },
    })
