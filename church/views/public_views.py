from datetime import date

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from church.forms import RequestForm
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
    church = get_object_or_404(Church, slug=slug, is_active=True)
    form = RequestForm(request.POST or None, church=church)
    if request.method == "POST" and form.is_valid():
        church_request = form.save(commit=False)
        church_request.church = church
        church_request.submitter_name = request.POST.get(
            "submitter_name", "").strip()
        church_request.submitter_contact = request.POST.get(
            "submitter_contact", "").strip()
        church_request.submitted_by = None
        church_request.save()
        return redirect("public_schedule", slug=church.slug)
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
