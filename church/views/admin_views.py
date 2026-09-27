import os
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.management import call_command

from church.forms import (
    AnnouncementForm,
    AssignmentForm,
    ChurchEventForm,
    ChurchSettingsForm,
    DepartmentForm,
    MemberEditForm,
    MemberInviteForm,
    RecalculateForm,
    RequestResponseForm,
    ServiceForm,
    ServiceItemForm,
)
from church.models import (
    AIInsight,
    Announcement,
    ChurchEvent,
    Department,
    Membership,
    Service,
    ServiceItem,
    Invitation,
)
from church.services.notifications import notify_department, notify_user
from church.services.recalculation import (
    freeze_service,
    recalculate_times,
    unfreeze_service,
)
from church.views.decorators import admin_required

User = get_user_model()


@admin_required
def admin_dashboard(request):
    """Show the signed-in coordinator a Monday-to-Sunday church calendar."""
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    services = request.church.services.filter(
        date__range=(week_start, week_end)
    ).prefetch_related("items")
    events = request.church.events.filter(
        date__range=(week_start, week_end)
    ).select_related("responsible_department")
    days = []
    for day_offset in range(7):
        day = week_start + timedelta(days=day_offset)
        days.append(
            {
                "date": day,
                "services": [service for service in services if service.date == day],
                "events": [event for event in events if event.date == day],
            }
        )
    return render(
        request,
        "church/dashboard.html",
        {
            "church": request.church,
            "today": today,
            "week_start": week_start,
            "week_end": week_end,
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
            "user_role_display": "Programme Coordinator",
        },
    )


@admin_required
def service_list(request):
    filter_name = request.GET.get("filter", "upcoming")
    services = request.church.services.prefetch_related("items__assignments").annotate(
        item_count=Count("items", distinct=True),
        assignment_count=Count("items__assignments", distinct=True),
    )
    today = timezone.localdate()
    if filter_name == "past":
        services = services.filter(date__lt=today)
    elif filter_name == "upcoming":
        services = services.filter(date__gte=today)
    return render(
        request,
        "church/service_list.html",
        {"services": services, "active_filter": filter_name,
            "current_year": timezone.localdate().year},
    )


@admin_required
@require_POST
def generate_year(request):
    year = int(request.POST.get("year", timezone.localdate().year))
    call_command("generate_year", church=request.church.slug, year=year)
    messages.success(request, f"Generated services for {year}.")
    return redirect("service_list")


@admin_required
def service_create(request):
    form = ServiceForm(request.POST or None, church=request.church)
    if request.method == "POST" and form.is_valid():
        service = form.save(commit=False)
        service.church = request.church
        service.status = "draft"
        service.save()
        if service.template:
            start = timezone.make_aware(
                datetime.combine(
                    service.date, service.template.default_start_time)
            )
            for template_item in service.template.items.select_related(
                "responsible_department"
            ):
                ServiceItem.objects.create(
                    service=service,
                    order=template_item.order,
                    title=template_item.title,
                    planned_start=start,
                    planned_duration_minutes=template_item.default_duration_minutes,
                    responsible_department=template_item.responsible_department,
                    notes=template_item.notes,
                )
                start += timedelta(minutes=template_item.default_duration_minutes)
        messages.success(request, "Service created.")
        return redirect("service_list")
    return render(request, "church/service_form.html", {"form": form, "title": "New service"})


@admin_required
def service_detail(request, pk):
    service = get_object_or_404(
        request.church.services.prefetch_related(
            "items__assignments", "items__responsible_department"
        ),
        pk=pk,
    )
    return render(
        request,
        "church/service_detail.html",
        {"service": service, "assignment_form": AssignmentForm()},
    )


@admin_required
def service_item_create(request, pk):
    service = get_object_or_404(request.church.services, pk=pk)
    form = ServiceItemForm(request.POST or None, church=request.church)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.service = service
        item.order = (service.items.order_by(
            "-order").first().order + 1) if service.items.exists() else 0
        item.save()
        notify_department(
            request.church,
            item.responsible_department,
            "New service item",
            f"{item.title} was added to {service.name}.",
        )
        messages.success(request, "Service item added.")
        return redirect("service_detail", pk=service.pk)
    return render(request, "church/service_item_form.html", {"form": form, "service": service, "title": "Add item"})


@admin_required
def service_item_edit(request, pk, item_pk):
    service = get_object_or_404(request.church.services, pk=pk)
    item = get_object_or_404(service.items, pk=item_pk)
    form = ServiceItemForm(request.POST or None,
                           instance=item, church=request.church)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        notify_department(
            request.church,
            item.responsible_department,
            "Service item updated",
            f"{item.title} in {service.name} was updated.",
        )
        messages.success(request, "Service item updated.")
        return redirect("service_detail", pk=service.pk)
    return render(request, "church/service_item_form.html", {"form": form, "service": service, "item": item, "title": "Edit item"})


@admin_required
@require_POST
def service_item_recalculate(request, pk, item_pk):
    service = get_object_or_404(request.church.services, pk=pk)
    item = get_object_or_404(service.items, pk=item_pk)
    form = RecalculateForm(request.POST)
    if form.is_valid():
        changed = recalculate_times(
            service,
            item,
            form.cleaned_data["actual_start"],
            user=request.user,
            reason=form.cleaned_data["reason"],
        )
        messages.success(request, f"Shifted {len(changed)} items.")
    else:
        messages.error(request, "Enter a valid time and reason.")
    return redirect("service_detail", pk=service.pk)


@admin_required
@require_POST
def service_freeze(request, pk):
    service = get_object_or_404(request.church.services, pk=pk)
    freeze_service(service, request.user)
    notify_user(
        request.user,
        "Bulletin frozen",
        f"{service.name} is now locked for publication.",
        url=f"/services/{service.pk}/",
        church=request.church,
    )
    messages.success(request, "Bulletin frozen.")
    return redirect("service_detail", pk=service.pk)


@admin_required
@require_POST
def service_unfreeze(request, pk):
    service = get_object_or_404(request.church.services, pk=pk)
    reason = request.POST.get("reason", "").strip()
    try:
        unfreeze_service(service, request.user, reason)
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Bulletin unfrozen.")
    return redirect("service_detail", pk=service.pk)


@admin_required
@require_POST
def assignment_create(request, pk, item_pk):
    service = get_object_or_404(request.church.services, pk=pk)
    item = get_object_or_404(service.items, pk=item_pk)
    form = AssignmentForm(request.POST)
    if form.is_valid():
        assignment = form.save(commit=False)
        assignment.service_item = item
        assignment.save()
        messages.success(request, "Assignment added.")
    else:
        messages.error(request, "Enter a name and role for the assignment.")
    return redirect("service_detail", pk=service.pk)


@admin_required
def event_create(request):
    form = ChurchEventForm(request.POST or None, church=request.church)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.church = request.church
        event.save()
        notify_department(
            request.church,
            event.responsible_department,
            "New church event",
            f"{event.title} is scheduled for {event.date}.",
        )
        messages.success(request, "Event created.")
        return redirect("admin_dashboard")
    return render(request, "church/event_form.html", {"form": form, "title": "New event"})


@admin_required
def event_edit(request, pk):
    event = get_object_or_404(request.church.events, pk=pk)
    form = ChurchEventForm(request.POST or None,
                           instance=event, church=request.church)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect("admin_dashboard")
    return render(request, "church/event_form.html", {"form": form, "event": event, "title": "Edit event"})


@admin_required
@require_POST
def event_delete(request, pk):
    event = get_object_or_404(request.church.events, pk=pk)
    event.delete()
    messages.success(request, "Event deleted.")
    return redirect("admin_dashboard")


@admin_required
def request_list(request):
    requests = request.church.requests.select_related(
        "submitted_by", "target_service"
    ).order_by("status", "-created_at")
    return render(request, "church/requests.html", {"requests": requests})


@admin_required
def request_respond(request, pk):
    church_request = get_object_or_404(request.church.requests, pk=pk)
    form = RequestResponseForm(request.POST or None, instance=church_request)
    if request.method == "POST" and form.is_valid():
        church_request = form.save(commit=False)
        church_request.responded_by = request.user
        church_request.responded_at = timezone.now()
        church_request.save()
        if church_request.submitted_by:
            notify_user(
                church_request.submitted_by,
                f"Request {church_request.status}",
                church_request.admin_response,
                church=request.church,
            )
        messages.success(request, "Request updated.")
        return redirect("request_list")
    return render(request, "church/request_respond.html", {"form": form, "church_request": church_request})


@admin_required
def department_list(request):
    departments = request.church.departments.all()
    return render(request, "church/departments.html", {"departments": departments})


@admin_required
def department_create(request):
    form = DepartmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        department = form.save(commit=False)
        department.church = request.church
        department.save()
        messages.success(request, "Department created.")
        return redirect("department_list")
    return render(request, "church/department_form.html", {"form": form, "title": "New department"})


@admin_required
def department_edit(request, pk):
    department = get_object_or_404(request.church.departments, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Department updated.")
        return redirect("department_list")
    return render(request, "church/department_form.html", {"form": form, "department": department, "title": "Edit department"})


@admin_required
def member_list(request):
    memberships = request.church.memberships.select_related(
        "user", "department", "invited_by")
    return render(request, "church/members.html", {"memberships": memberships})


@admin_required
def member_invite(request):
    import secrets
    from django.core.mail import send_mail
    from django.urls import reverse

    form = MemberInviteForm(request.POST or None, church=request.church)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        token = secrets.token_urlsafe(32)
        Invitation.objects.create(
            church=request.church,
            email=data["email"],
            role=data["role"],
            department=data.get("department"),
            token=token,
            invited_by=request.user,
        )
        accept_url = request.build_absolute_uri(
            reverse("accept_invitation", kwargs={"token": token})
        )
        send_mail(
            subject=f"You're invited to join {request.church.name} on Harpr",
            message=(
                f"{request.user.get_full_name() or request.user.username} "
                f"has invited you to join {request.church.name} on Harpr.\n\n"
                f"Click this link to set your password and accept:\n{accept_url}\n\n"
                f"This link expires in 7 days."
            ),
            from_email="harpr@localhost",
            recipient_list=[data["email"]],
            fail_silently=False,
        )
        messages.success(request, f"Invitation sent to {data['email']}.")
        return redirect("member_list")
    return render(request, "church/member_form.html", {"form": form, "title": "Invite member"})


@admin_required
def member_edit(request, pk):
    membership = get_object_or_404(
        request.church.memberships.select_related("user"), pk=pk)
    form = MemberEditForm(
        request.POST or None,
        church=request.church,
        initial={
            "email": membership.user.email,
            "first_name": membership.user.first_name,
            "last_name": membership.user.last_name,
            "role": membership.role,
            "department": membership.department_id,
        },
    )
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        membership.user.email = data["email"]
        membership.user.first_name = data["first_name"]
        membership.user.last_name = data["last_name"]
        membership.user.save(
            update_fields=["email", "first_name", "last_name"])
        membership.role = data["role"]
        membership.department = data["department"]
        membership.save(update_fields=["role", "department"])
        messages.success(request, "Member updated.")
        return redirect("member_list")
    return render(request, "church/member_form.html", {"form": form, "membership": membership, "title": "Edit member"})


@admin_required
@require_POST
def member_deactivate(request, pk):
    membership = get_object_or_404(request.church.memberships, pk=pk)
    membership.is_active = False
    membership.save(update_fields=["is_active"])
    messages.success(request, "Member deactivated.")
    return redirect("member_list")


@admin_required
def announcement_list(request):
    announcements = request.church.announcements.select_related("service")
    return render(request, "church/announcements.html", {"announcements": announcements})


@admin_required
def announcement_create(request):
    form = AnnouncementForm(request.POST or None, church=request.church)
    if request.method == "POST" and form.is_valid():
        announcement = form.save(commit=False)
        announcement.church = request.church
        announcement.save()
        messages.success(request, "Announcement created.")
        return redirect("announcement_list")
    return render(request, "church/announcement_form.html", {"form": form, "title": "New announcement"})


@admin_required
def announcement_edit(request, pk):
    announcement = get_object_or_404(request.church.announcements, pk=pk)
    form = AnnouncementForm(request.POST or None,
                            instance=announcement, church=request.church)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Announcement updated.")
        return redirect("announcement_list")
    return render(request, "church/announcement_form.html", {"form": form, "announcement": announcement, "title": "Edit announcement"})


def gather_church_stats(church):
    services = list(
        church.services.filter(status="completed").prefetch_related(
            "items__responsible_department"
        ).order_by("-date")[:12]
    )
    delays = []
    overruns = []
    item_delays = {}
    overrun_services = 0
    for service in services:
        service_overran = False
        for item in service.items.all():
            if item.actual_start and item.planned_start:
                delay = (item.actual_start -
                         item.planned_start).total_seconds() / 60
                delays.append(delay)
                item_delays.setdefault(item.title, []).append(delay)
            if item.actual_duration_minutes is not None:
                overrun = item.actual_duration_minutes - item.planned_duration_minutes
                overruns.append(overrun)
                service_overran = service_overran or overrun > 0
        if service_overran:
            overrun_services += 1
    most_delayed = "N/A"
    if item_delays:
        most_delayed = max(
            item_delays,
            key=lambda title: sum(
                item_delays[title]) / len(item_delays[title]),
        )
    return {
        "service_count": len(services),
        "avg_delay_minutes": round(sum(delays) / len(delays), 1) if delays else 0,
        "avg_overrun_minutes": round(sum(overruns) / len(overruns), 1) if overruns else 0,
        "most_delayed_item": most_delayed,
        "overrun_count": overrun_services,
    }


@admin_required
def ai_insights(request):
    cutoff = timezone.now() - timedelta(hours=24)
    cached = request.church.ai_insights.filter(
        generated_at__gte=cutoff).first()
    if cached:
        return render(
            request,
            "church/ai_insights.html",
            {"insight": cached.content, "stats": cached.raw_stats, "cached": True},
        )
    stats = gather_church_stats(request.church)
    if stats["service_count"] < 3:
        return render(
            request,
            "church/ai_insights.html",
            {
                "insight": "Not enough data yet. Complete at least 3 services to see AI insights.",
                "stats": stats,
                "cached": False,
            },
        )
    insight_text = ""
    try:
        from openai import OpenAI

        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ.get("GROQ_API_KEY") or None,
        )
        prompt = (
            "Analyse these aggregated church operations numbers and give three "
            "specific recommendations under 150 words. "
            f"Data: {stats}"
        )
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a church operations analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        insight_text = response.choices[0].message.content
    except Exception:
        insight_text = "AI analysis temporarily unavailable."
    AIInsight.objects.create(
        church=request.church,
        period_start=timezone.localdate() - timedelta(days=30),
        period_end=timezone.localdate(),
        content=insight_text,
        raw_stats=stats,
    )
    return render(
        request,
        "church/ai_insights.html",
        {"insight": insight_text, "stats": stats, "cached": False},
    )


@admin_required
def church_settings(request):
    form = ChurchSettingsForm(request.POST or None,
                              request.FILES or None, instance=request.church)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Church settings saved.")
        return redirect("church_settings")
    return render(request, "church/settings.html", {"form": form, "church": request.church})
