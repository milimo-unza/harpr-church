from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from church.forms import AssignmentForm, RequestForm
from church.models import ServiceItem
from church.views.decorators import dept_head_required


@dept_head_required
def dept_dashboard(request):
    if not request.department:
        items = ServiceItem.objects.none()
    else:
        items = (
            ServiceItem.objects.filter(
                church=request.church,
                responsible_department=request.department,
                planned_start__gte=timezone.now(),
            )
            .select_related("service")
            .prefetch_related("assignments")
            .order_by("planned_start")
        )
    pending_items = [item for item in items if not item.assignments.exists()]
    return render(
        request,
        "church/dept_dashboard.html",
        {"items": items, "pending_items": pending_items},
    )


@dept_head_required
def dept_item_detail(request, pk):
    item = get_object_or_404(
        ServiceItem.objects.select_related("service", "responsible_department"),
        pk=pk,
        church=request.church,
        responsible_department=request.department,
    )
    return render(
        request,
        "church/dept_item_detail.html",
        {"item": item, "form": AssignmentForm()},
    )


@dept_head_required
@require_POST
def dept_assignment_create(request, pk):
    item = get_object_or_404(
        ServiceItem,
        pk=pk,
        church=request.church,
        responsible_department=request.department,
    )
    form = AssignmentForm(request.POST)
    if form.is_valid():
        assignment = form.save(commit=False)
        assignment.service_item = item
        assignment.save()
        messages.success(request, "Assignment added.")
    else:
        messages.error(request, "Enter a name and role.")
    return redirect("dept_item_detail", pk=item.pk)


@dept_head_required
def dept_request_create(request):
    form = RequestForm(request.POST or None, church=request.church)
    if request.method == "POST" and form.is_valid():
        church_request = form.save(commit=False)
        church_request.church = request.church
        church_request.submitted_by = request.user
        church_request.save()
        messages.success(request, "Request submitted.")
        return redirect("dept_request_list")
    return render(request, "church/dept_request_form.html", {"form": form})


@dept_head_required
def dept_request_list(request):
    requests = request.church.requests.filter(submitted_by=request.user)
    return render(request, "church/dept_requests.html", {"requests": requests})