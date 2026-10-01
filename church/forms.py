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
    ServiceTemplate,
)

User = get_user_model()


def _style_fields(form):
    for field in form.fields.values():
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing} form-input".strip()


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
        _style_fields(self)


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

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible_department"].queryset = (
            church.departments.all() if church else Department.objects.none()
        )
        _style_fields(self)


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["person_name", "role", "phone", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class RequestForm(forms.ModelForm):
    """Department head submission. Two types: announcement, schedule."""

    class Meta:
        model = Request
        fields = ["type", "title", "body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


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
        _style_fields(self)


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
        fields = ["name", "slug", "description", "color"]
        widgets = {"description": forms.Textarea(
            attrs={"rows": 3}), "color": forms.TextInput(attrs={"type": "color"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


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
        _style_fields(self)


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
        _style_fields(self)


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
        _style_fields(self)


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
        _style_fields(self)

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
        _style_fields(self)


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
        _style_fields(self)


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
        return church, user
