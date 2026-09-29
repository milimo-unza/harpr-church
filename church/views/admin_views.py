import json
import os
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.management import call_command

from django.conf import settings

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


def _is_ajax(request):
    """True if the request came from our modal JS (fetch + X-Requested-With)."""
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.headers.get("Accept", "").startswith("application/json")
    )


def _form_errors_json(form):
    """Flatten Django form errors into {field: [messages]}."""
    return {field: [str(e) for e in errs] for field, errs in form.errors.items()}


@admin_required
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

    month_start = today.replace(day=1)
    # Last day of month: first day of next month minus one day
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    month_end = next_month - timedelta(days=1)

    return render(request, "church/dashboard.html", {
        "church": request.church,
        "today": today,
        "week_start": week_start,
        "week_end": week_end,
        "prev_week": prev_week,
        "next_week": next_week,
        "days": days,
        "service_count": request.church.services.filter(
            date__gte=month_start, date__lte=month_end
        ).count(),
        "month_label": today.strftime("%b %Y"),
        "completed_count": request.church.services.filter(
            status="completed"
        ).count(),
        "pending_request_count": request.church.requests.filter(
            status="pending"
        ).count(),
        "recent_activity": request.church.logs.select_related(
            "user", "service", "service_item"
        )[:20],
        "service_templates": request.church.service_templates.filter(is_active=True),
        "departments": request.church.departments.all(),
    })


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
        {
            "services": services,
            "active_filter": filter_name,
            "current_year": timezone.localdate().year,
            "service_form": ServiceForm(church=request.church),
            "service_templates": request.church.service_templates.filter(is_active=True),
        },
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
        if _is_ajax(request):
            return JsonResponse({
                "ok": True,
                "redirect": "/services/",
                "message": "Service created.",
            })
        messages.success(request, "Service created.")
        return redirect("service_list")

    if request.method == "POST" and _is_ajax(request):
        return JsonResponse({"ok": False, "errors": _form_errors_json(form)}, status=400)

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
        {
            "service": service,
            "assignment_form": AssignmentForm(),
            "item_form": ServiceItemForm(church=request.church),
            "departments": request.church.departments.all(),
        },
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
        if _is_ajax(request):
            return JsonResponse({
                "ok": True,
                "redirect": f"/services/{service.pk}/",
                "message": "Service item added.",
            })
        messages.success(request, "Service item added.")
        return redirect("service_detail", pk=service.pk)

    if request.method == "POST" and _is_ajax(request):
        return JsonResponse({"ok": False, "errors": _form_errors_json(form)}, status=400)

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
        if _is_ajax(request):
            return JsonResponse({
                "ok": True,
                "redirect": f"/services/{service.pk}/",
                "message": "Service item updated.",
            })
        messages.success(request, "Service item updated.")
        return redirect("service_detail", pk=service.pk)

    if request.method == "POST" and _is_ajax(request):
        return JsonResponse({"ok": False, "errors": _form_errors_json(form)}, status=400)

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
        if _is_ajax(request):
            return JsonResponse({
                "ok": True,
                "redirect": "/dashboard/",
                "message": "Event created.",
            })
        messages.success(request, "Event created.")
        return redirect("admin_dashboard")

    if request.method == "POST" and _is_ajax(request):
        return JsonResponse({"ok": False, "errors": _form_errors_json(form)}, status=400)

    return render(request, "church/event_form.html", {"form": form, "title": "New event"})


@admin_required
def event_edit(request, pk):
    event = get_object_or_404(request.church.events, pk=pk)
    form = ChurchEventForm(request.POST or None,
                           instance=event, church=request.church)
    if request.method == "POST" and form.is_valid():
        form.save()
        if _is_ajax(request):
            return JsonResponse({
                "ok": True,
                "redirect": "/dashboard/",
                "message": "Event updated.",
            })
        messages.success(request, "Event updated.")
        return redirect("admin_dashboard")

    if request.method == "POST" and _is_ajax(request):
        return JsonResponse({"ok": False, "errors": _form_errors_json(form)}, status=400)

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
    if request.method == "POST":
        messages.error(request, "Please correct the errors in the form.")
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
    if request.method == "POST":
        messages.error(request, "Please correct the errors in the form.")
        return redirect("department_list")
    return render(request, "church/department_form.html", {"form": form, "department": department, "title": "Edit department"})


@admin_required
@require_POST
def department_delete(request, pk):
    department = get_object_or_404(request.church.departments, pk=pk)
    department.delete()
    messages.success(request, "Department deleted.")
    return redirect("department_list")


@admin_required
def member_list(request):
    memberships = (
        request.church.memberships
        .select_related("user", "department", "invited_by")
        .order_by("is_active", "user__username")
    )
    departments = request.church.departments.all()

    return render(request, "church/members.html", {
        "memberships": memberships,
        "departments": departments,
    })


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
                f"Click this link to set your password and accept:\n"
                f"{accept_url}\n\n"
                f"This link expires in 7 days and can only be used once."
            ),
            from_email="harpr@localhost",
            recipient_list=[data["email"]],
            fail_silently=False,
        )
        messages.success(request, f"Invitation sent to {data['email']}.")
        return redirect("member_list")
    return render(
        request,
        "church/member_form.html",
        {"form": form, "title": "Invite member"},
    )


@admin_required
def member_edit(request, pk):
    membership = get_object_or_404(
        request.church.memberships.select_related("user"), pk=pk
    )
    form = MemberEditForm(
        request.POST or None,
        church=request.church,
        initial={
            "role": membership.role,
            "department": membership.department_id,
        },
    )
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        if membership.user == request.user and data["role"] != "admin":
            messages.error(request, "You cannot change your own role from Administrator.")
            return redirect("member_list")
        membership.role = data["role"]
        membership.department = data["department"]
        membership.save(update_fields=["role", "department"])

        notify_user(
            membership.user,
            "Your role has been updated",
            f"Your role in {request.church.name} is now {membership.get_role_display()}.",
            church=request.church,
        )
        messages.success(request, "Member updated.")
        return redirect("member_list")
    return render(request, "church/member_form.html", {"form": form, "membership": membership, "title": "Edit member"})


@admin_required
@require_POST
def member_deactivate(request, pk):
    membership = get_object_or_404(request.church.memberships, pk=pk)
    if membership.user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("member_list")
    membership.is_active = False
    membership.save(update_fields=["is_active"])

    notify_user(
        membership.user,
        "Your account has been deactivated",
        f"Your access to {request.church.name} has been suspended by an administrator.",
        church=request.church,
    )
    messages.success(request, f"{membership.user.username} deactivated.")
    return redirect("member_list")


@admin_required
@require_POST
def member_reactivate(request, pk):
    from django.contrib.auth import authenticate

    membership = get_object_or_404(request.church.memberships, pk=pk)
    password = request.POST.get("admin_password", "")

    if not authenticate(
        request, username=request.user.username, password=password
    ):
        messages.error(
            request,
            "Incorrect password. Reactivation cancelled.",
        )
        return redirect("member_list")

    membership.is_active = True
    membership.save(update_fields=["is_active"])

    notify_user(
        membership.user,
        "Your account has been reactivated",
        f"Your access to {request.church.name} has been restored.",
        church=request.church,
    )
    messages.success(request, f"{membership.user.username} reactivated.")
    return redirect("member_list")


@admin_required
def announcement_list(request):
    today = timezone.localdate()
    all_announcements = request.church.announcements.all()

    active = all_announcements.filter(
        start_date__lte=today,
        end_date__gte=today,
    ).order_by("start_date")

    upcoming = all_announcements.filter(
        start_date__gt=today,
    ).order_by("start_date")

    older = all_announcements.filter(
        end_date__lt=today,
    ).order_by("-end_date")

    return render(request, "church/announcements.html", {
        "active_announcements": active,
        "upcoming_announcements": upcoming,
        "older_announcements": older,
    })


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


@admin_required
@require_POST
def announcement_pause(request, pk):
    announcement = get_object_or_404(request.church.announcements, pk=pk)
    announcement.is_paused = not announcement.is_paused
    announcement.save(update_fields=["is_paused"])
    state = "paused" if announcement.is_paused else "resumed"
    messages.success(request, f"Announcement {state}.")
    return redirect("announcement_list")


@admin_required
@require_POST
def announcement_delete(request, pk):
    announcement = get_object_or_404(request.church.announcements, pk=pk)
    announcement.delete()
    messages.success(request, "Announcement deleted.")
    return redirect("announcement_list")


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
    if cached and "temporarily unavailable" not in cached.content:
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

    api_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return render(
            request,
            "church/ai_insights.html",
            {
                "insight": (
                    "AI insights are disabled because no Groq API key is configured. "
                    "Set the GROQ_API_KEY environment variable (or add it to your .env file) "
                    "and reload this page. Everything else in Harpr works without it."
                ),
                "stats": stats,
                "cached": False,
                "no_key": True,
            },
        )

    insight_text = ""
    error_detail = ""
    try:
        from openai import OpenAI

        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )
        prompt = (
            "You are writing a short plain-prose paragraph for a church "
            "programme coordinator. Do not use markdown, bullet points, "
            "headings, or asterisks — just flowing sentences. Write 3 to 5 "
            "sentences. First summarise what the numbers show, then name the "
            "single item with the largest average delay, then suggest one "
            "concrete thing the coordinator could adjust. If a number is zero "
            "or unavailable, do not invent a finding about it. "
            f"Aggregated summary numbers: {stats}"
        )
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a church operations analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=400,
        )
        insight_text = response.choices[0].message.content
    except Exception as exc:
        error_detail = f"{type(exc).__name__}: {exc}"
        insight_text = (
            "AI analysis is temporarily unavailable. "
            f"({error_detail})"
        )

    if not error_detail:
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
        {
            "insight": insight_text,
            "stats": stats,
            "cached": False,
            "error_detail": error_detail,
        },
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
