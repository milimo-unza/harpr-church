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
            church.service_templates.filter(is_active=True) if church else ServiceTemplate.objects.none()
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
    class Meta:
        model = Request
        fields = ["type", "title", "body", "target_service"]
        widgets = {"body": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target_service"].required = False
        self.fields["target_service"].queryset = (
            church.services.all() if church else Service.objects.none()
        )
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


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "slug", "description", "color"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3}), "color": forms.TextInput(attrs={"type": "color"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class MemberInviteForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    role = forms.ChoiceField(choices=Membership.ROLE_CHOICES)
    department = forms.ModelChoiceField(queryset=Department.objects.none(), required=False)

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = (
            church.departments.all() if church else Department.objects.none()
        )
        _style_fields(self)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already in use.")
        return username


class MemberEditForm(forms.Form):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    role = forms.ChoiceField(choices=Membership.ROLE_CHOICES)
    department = forms.ModelChoiceField(queryset=Department.objects.none(), required=False)

    def __init__(self, *args, church=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = (
            church.departments.all() if church else Department.objects.none()
        )
        _style_fields(self)


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "body", "service", "show_on_public", "expires_at"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4}),
            "expires_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
            ),
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
    timezone = forms.ChoiceField(choices=AFRICAN_TIMEZONES, initial="Africa/Lusaka")

    class Meta:
        model = Church
        fields = ["name", "slug", "timezone", "address", "phone", "email", "logo"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)