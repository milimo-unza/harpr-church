from datetime import time as _time, timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from church.models import (
    Announcement,
    Assignment,
    Church,
    ChurchEvent,
    Department,
    Membership,
    Request,
    Service,
    ServiceItem,
    ServiceItemTemplate,
    ServiceTemplate,
)

User = get_user_model()


class ServiceTemplateForm(forms.ModelForm):
    class Meta:
        model = ServiceTemplate
        fields = [
            "name",
            "day_of_week",
            "default_start_time",
            "default_duration_minutes",
            "is_active",
        ]
        widgets = {
            "default_start_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_input_class(self)


class ServiceItemTemplateForm(forms.ModelForm):
    class Meta:
        model = ServiceItemTemplate
        fields = [
            "title",
            "default_duration_minutes",
            "responsible_department",
            "notes",
        ]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible_department"].queryset = (
            church.departments.all() if church else Department.objects.none()
        )
        add_input_class(self)


class ServiceForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=ServiceTemplate.objects.none(), required=False
    )

    class Meta:
        model = Service
        fields = ["name", "date", "template"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["template"].queryset = (
            church.service_templates.filter(
                is_active=True) if church else ServiceTemplate.objects.none()
        )
        add_input_class(self)


class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = [
            "title",
            "planned_start",
            "planned_duration_minutes",
            "responsible_department",
            "notes",
            "lock_actual_start",
        ]
        widgets = {
            "planned_start": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, church=None, service=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = service
        if not self.instance.pk:
            if self.service and self.service.items.exists():
                last_item = self.service.items.order_by("-order").first()
                if last_item:
                    default_start = last_item.planned_start + timedelta(
                        minutes=last_item.planned_duration_minutes or 0
                    )
                    self.fields["planned_start"].initial = default_start.strftime(
                        "%Y-%m-%dT%H:%M"
                    )
                else:
                    self.fields["planned_start"].initial = timezone.localtime().strftime(
                        "%Y-%m-%dT%H:%M"
                    )
            else:
                self.fields["planned_start"].initial = timezone.localtime().strftime(
                    "%Y-%m-%dT%H:%M"
                )
        self.fields["responsible_department"].queryset = (
            church.departments.all() if church else Department.objects.none()
        )
        add_input_class(self)

    def clean(self):
        cleaned = super().clean()
        if not self.service:
            return cleaned

        start = cleaned.get("planned_start")
        duration = cleaned.get("planned_duration_minutes")
        if not start or duration is None:
            return cleaned

        stop = start + timedelta(minutes=duration)
        overlaps = []
        for item in self.service.items.exclude(pk=self.instance.pk):
            item_stop = item.planned_start + timedelta(
                minutes=item.planned_duration_minutes or 0
            )
            if start < item_stop and stop > item.planned_start:
                overlaps.append(item.title)

        if overlaps:
            raise forms.ValidationError(
                f"Overlaps with: {', '.join(overlaps)}")
        return cleaned


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["person_name", "role", "phone", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_input_class(self)


class RequestForm(forms.ModelForm):
    """Department head submission. Two types: announcement, schedule."""

    class Meta:
        model = Request
        fields = ["type", "title", "body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        add_input_class(self)


class RequestResponseForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ["status", "admin_response"]
        widgets = {"admin_response": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ]
        add_input_class(self)


class RequestApproveForm(forms.Form):
    """Coordinator's response. `approved_text` is required only for
    announcement approvals — it becomes the public announcement body.
    Schedule approvals treat it as optional notes."""

    status = forms.ChoiceField(choices=[
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ])
    approved_text = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
        label="Your wording",
    )

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")
        req_type = self.data.get("request_type", "")
        text = (cleaned.get("approved_text") or "").strip()
        if status == "approved" and req_type == "announcement" and not text:
            raise forms.ValidationError(
                "Please write your own wording before approving."
            )
        return cleaned


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "slug", "description"]
        widgets = {"description": forms.Textarea(
            attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_input_class(self)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        qs = Department.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "A department with this name already exists.")
        return name


class MemberInviteForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=Membership.ROLE_CHOICES)
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(), required=False
    )

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = (
            church.departments.all() if church else Department.objects.none()
        )
        add_input_class(self)


class MemberEditForm(forms.Form):
    role = forms.ChoiceField(choices=Membership.ROLE_CHOICES)
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(), required=False
    )

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = (
            church.departments.all() if church else Department.objects.none()
        )
        add_input_class(self)


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            "body",
            "service",
            "show_on_public",
            "start_date",
            "end_date",
            "is_paused",
        ]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].required = False
        self.fields["service"].queryset = (
            church.services.all() if church else Service.objects.none()
        )
        add_input_class(self)


class ChurchEventForm(forms.ModelForm):
    class Meta:
        model = ChurchEvent
        fields = [
            "title",
            "event_type",
            "date",
            "start_time",
            "end_time",
            "location",
            "responsible_department",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
            "end_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible_department"].queryset = (
            church.departments.all() if church else Department.objects.none()
        )
        add_input_class(self)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("start_time") and cleaned.get("end_time") and cleaned["end_time"] <= cleaned["start_time"]:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned


class RecalculateForm(forms.Form):
    actual_start = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
        )
    )
    reason = forms.CharField(max_length=500)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_input_class(self)


class ChurchSettingsForm(forms.ModelForm):
    AFRICAN_TIMEZONES = [
        ("Africa/Lusaka", "Africa/Lusaka"),
        ("Africa/Johannesburg", "Africa/Johannesburg"),
        ("Africa/Nairobi", "Africa/Nairobi"),
        ("Africa/Accra", "Africa/Accra"),
        ("Africa/Cairo", "Africa/Cairo"),
        ("Africa/Lagos", "Africa/Lagos"),
    ]
    timezone = forms.ChoiceField(
        choices=AFRICAN_TIMEZONES, initial="Africa/Lusaka"
    )

    class Meta:
        model = Church
        fields = [
            "name", "slug", "worship_day", "timezone", "address",
            "phone", "email", "logo",
            "contact_phone", "contact_email", "contact_whatsapp",
            "footer_verse",
        ]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_input_class(self)


class ChurchSignupForm(forms.Form):
    church_name = forms.CharField(max_length=200)
    church_slug = forms.SlugField(max_length=100)
    church_address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}), required=False
    )
    worship_day = forms.ChoiceField(
        choices=Church.WORSHIP_DAY_CHOICES, initial=6
    )
    coordinator_username = forms.CharField(max_length=150)
    coordinator_email = forms.EmailField()
    coordinator_first_name = forms.CharField(max_length=150)
    coordinator_last_name = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_church_slug(self):
        slug = self.cleaned_data["church_slug"]
        if Church.objects.filter(slug=slug).exists():
            raise forms.ValidationError("That church URL is already taken.")
        return slug

    def clean_coordinator_username(self):
        username = self.cleaned_data["coordinator_username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("The two passwords don't match.")
        if p1 and len(p1) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters.")
        return cleaned

    def save(self):
        from django.db import transaction
        with transaction.atomic():
            church = Church.objects.create(
                name=self.cleaned_data["church_name"],
                slug=self.cleaned_data["church_slug"],
                address=self.cleaned_data.get("church_address", ""),
                worship_day=int(self.cleaned_data["worship_day"]),
                # hardcoded for Zambia, add a picker later
                timezone="Africa/Lusaka",
            )
            user = User.objects.create_user(
                username=self.cleaned_data["coordinator_username"],
                email=self.cleaned_data["coordinator_email"],
                first_name=self.cleaned_data["coordinator_first_name"],
                last_name=self.cleaned_data["coordinator_last_name"],
                password=self.cleaned_data["password1"],
            )
            Membership.objects.create(user=user, church=church, role="admin")
            for slug, name in Department.DEFAULT_DEPARTMENTS:
                Department.objects.create(church=church, slug=slug, name=name)

            starter = ServiceTemplate.objects.create(
                church=church,
                name="Sunday Worship Service",
                day_of_week=int(church.worship_day),
                default_start_time=_time(8, 0),
                default_duration_minutes=120,
                is_active=True,
            )
            for order, (title, minutes, slug) in enumerate([
                ("Opening Prayer", 10, "pastors"),
                ("Worship Songs", 25, "music"),
                ("Sermon", 45, "pastors"),
                ("Announcements", 10, "pastors"),
                ("Benediction", 5, "pastors"),
            ]):
                ServiceItemTemplate.objects.create(
                    template=starter,
                    order=order,
                    title=title,
                    default_duration_minutes=minutes,
                    responsible_department=Department.objects.get(
                        church=church, slug=slug
                    ),
                )
        return church, user


class PublicRequestForm(forms.ModelForm):
    """Used by the public. Announcements only.

    Validates name, contact (email or phone), title, body, and date range.
    """

    submitter_name = forms.CharField(
        max_length=200, required=True, label="Your name"
    )
    submitter_contact = forms.CharField(
        max_length=200, required=True, label="Contact (phone or email)"
    )
    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Start date",
    )
    end_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="End date",
    )

    class Meta:
        model = Request
        fields = ["title", "body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 5})}

    def clean_submitter_contact(self):
        import re
        contact = (self.cleaned_data.get("submitter_contact") or "").strip()
        if not contact:
            raise forms.ValidationError("Enter a phone number or email.")
        email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        if email_re.match(contact):
            return contact
        if not re.match(r"^[+\d][\d\s\-()]*$", contact):
            raise forms.ValidationError(
                "Enter a valid phone number or email address."
            )
        digits = re.sub(r"\D", "", contact)
        is_international = contact.startswith("+")
        if is_international:
            # E.164-ish: 11-15 digits after the plus.
            if not (11 <= len(digits) <= 15):
                raise forms.ValidationError(
                    "International number must have 11 to 15 digits."
                )
        else:
            if len(digits) != 10:
                raise forms.ValidationError(
                    "Phone number must be exactly 10 digits, or start with + "
                    "for an international number."
                )
        return contact

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        if start and end and end < start:
            raise forms.ValidationError(
                "End date must be on or after the start date."
            )
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.type = "announcement"
        if commit:
            obj.save()
        return obj

# Quick way to give every field the same css class without listing them


def add_input_class(form):
    for f in form.fields.values():
        f.widget.attrs["class"] = "form-input"
