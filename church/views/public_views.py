from datetime import date

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from church.forms import PublicRequestForm, RequestForm
from church.models import Church, Service
from church.services.pdf import generate_bulletin_pdf
from church.services.qr import generate_qr_png


def _public_service_context(church, target_date):
    service = (
        church.services.filter(date=target_date)
        .prefetch_related("items__assignments", "items__responsible_department")
        .first()
    )
    next_service = None
    if not service:
        next_service = (
            church.services.filter(date__gt=target_date)
            .order_by("date")
            .first()
        )
    today = timezone.localdate()
    announcements = church.announcements.filter(
        is_paused=False,
        show_on_public=True,
        start_date__lte=today,
        end_date__gte=today,
    ).order_by("start_date")
    return {
        "church": church,
        "service": service,
        "next_service": next_service,
        "announcements": announcements,
        "target_date": target_date,
    }


def public_schedule(request, slug):
    church = get_object_or_404(Church, slug=slug, is_active=True)
    return render(
        request,
        "church/public_schedule.html",
        _public_service_context(church, timezone.localdate()),
    )


def public_schedule_date(request, slug, year, month, day):
    church = get_object_or_404(Church, slug=slug, is_active=True)
    target = get_object_or_404_date(year, month, day)
    return render(
        request,
        "church/public_schedule.html",
        _public_service_context(church, target),
    )


def get_object_or_404_date(year, month, day):
    try:
        return date(year, month, day)
    except ValueError:
        from django.http import Http404

        raise Http404("Invalid date.")


def public_request(request, slug):
    from django.contrib import messages

    church = get_object_or_404(Church, slug=slug, is_active=True)
    form = PublicRequestForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        church_request = form.save(commit=False)
        church_request.church = church
        church_request.type = "announcement"
        church_request.submitter_name = request.POST.get(
            "submitter_name", "").strip()
        church_request.submitter_contact = request.POST.get(
            "submitter_contact", "").strip()
        church_request.submitted_by = None

        # TODO: this parsing should be a form, not manual
        start_raw = request.POST.get("start_date", "").strip()
        end_raw = request.POST.get("end_date", "").strip()
        if start_raw:
            try:
                church_request.start_date = date.fromisoformat(start_raw)
            except ValueError:
                pass
        if end_raw:
            try:
                church_request.end_date = date.fromisoformat(end_raw)
            except ValueError:
                pass

        church_request.save()
        messages.success(
            request,
            "Thank you. Your request has been sent to the programme "
            "coordinator for review.",
        )
        return redirect("public_schedule", slug=church.slug)

    if request.method == "POST":
        # Show the first error so the user knows what went wrong.
        errors = []
        for field_errors in form.errors.values():
            errors.extend([str(e) for e in field_errors])
        # Also collect errors from the manual fields we validate below.
        if errors:
            messages.error(request, errors[0])

    return render(
        request,
        "church/public_request_form.html",
        {"form": form, "church": church},
    )


def public_bulletin_pdf(request, slug, year, month, day):
    church = get_object_or_404(Church, slug=slug, is_active=True)
    target = get_object_or_404_date(year, month, day)
    service = get_object_or_404(church.services, date=target)
    buffer = generate_bulletin_pdf(service)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="bulletin-{target.isoformat()}.pdf"'
    )
    return response


def church_qr(request, slug):
    church = get_object_or_404(Church, slug=slug, is_active=True)
    url = request.build_absolute_uri(
        reverse("public_schedule", kwargs={"slug": church.slug})
    )
    return HttpResponse(generate_qr_png(url).getvalue(), content_type="image/png")


def terms(request):
    return render(request, "public/terms.html")


def privacy(request):
    return render(request, "public/privacy.html")
