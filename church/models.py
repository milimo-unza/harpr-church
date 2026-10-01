from django.conf import settings
from django.db import models


class Church(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    timezone = models.CharField(max_length=50, default="Africa/Lusaka")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    WORSHIP_DAY_CHOICES = [
        (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"),
        (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday"),
    ]
    worship_day = models.PositiveSmallIntegerField(
        choices=WORSHIP_DAY_CHOICES, default=6,
        help_text="The church's main day of worship.",
    )
    logo = models.ImageField(upload_to="church_logos/", blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_whatsapp = models.CharField(max_length=30, blank=True)
    footer_verse = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = [
        ("admin", "Programme Coordinator"),
        ("dept_head", "Department Head"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="church_memberships",
    )
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="dept_head")
    department = models.ForeignKey(
        "Department", on_delete=models.SET_NULL, null=True, blank=True
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invited_members",
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("user", "church")]

    def __str__(self):
        return f"{self.user.username} @ {self.church.name} ({self.role})"


class Department(models.Model):
    DEFAULT_DEPARTMENTS = [
        ("pastors", "Pastors / Preaching"),
        ("music", "Music / Worship"),
        ("ushering", "Ushering"),
        ("media", "Media / Sound / Tech"),
        ("children", "Children's Ministry"),
        ("prayer", "Prayer Ministry"),
        ("finance", "Finance / Administration"),
        ("youth", "Youth Ministry"),
    ]

    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="departments"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#b5623e")
    is_custom = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("church", "slug")]

    def __str__(self):
        return f"{self.church.name} — {self.name}"


class DepartmentMember(models.Model):
    """A saved person in a department's roster.

    Purely a convenience feature: department heads click a saved name to
    pre-fill an assignment instead of retyping it. Assignments themselves
    stay free-text so this model has no impact on existing data."""

    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="department_members"
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="roster"
    )
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("department", "name")]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class ServiceTemplate(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="service_templates"
    )
    name = models.CharField(max_length=200)
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    default_start_time = models.TimeField()
    default_duration_minutes = models.PositiveIntegerField(default=120)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_day_of_week_display()})"


class ServiceItemTemplate(models.Model):
    template = models.ForeignKey(
        ServiceTemplate, on_delete=models.CASCADE, related_name="items"
    )
    church = models.ForeignKey(
        Church,
        on_delete=models.CASCADE,
        related_name="service_item_templates",
        editable=False,
    )
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200)
    default_duration_minutes = models.PositiveIntegerField(default=10)
    responsible_department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        self.church_id = self.template.church_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.template.name} — {self.title}"


class Service(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("frozen", "Frozen (Bulletin Locked)"),
        ("completed", "Completed"),
    ]

    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="services"
    )
    template = models.ForeignKey(
        ServiceTemplate, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=200)
    date = models.DateField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft")
    frozen_at = models.DateTimeField(null=True, blank=True)
    frozen_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    unfrozen_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.name} — {self.date}"


class ServiceItem(models.Model):
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("skipped", "Skipped"),
        ("changed", "Changed"),
    ]

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="items")
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="service_items", editable=False
    )
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200)
    planned_start = models.DateTimeField()
    planned_duration_minutes = models.PositiveIntegerField(default=10)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_duration_minutes = models.PositiveIntegerField(
        null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="planned")
    responsible_department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    lock_actual_start = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        self.church_id = self.service.church_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service.name} — {self.title}"


class Assignment(models.Model):
    service_item = models.ForeignKey(
        ServiceItem, on_delete=models.CASCADE, related_name="assignments"
    )
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="assignments", editable=False
    )
    person_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.church_id = self.service_item.church_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.person_name} — {self.role}"


class Person(models.Model):
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="people")
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Request(models.Model):
    TYPE_CHOICES = [
        ("announcement", "Announcement"),
        ("schedule", "Add to schedule"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="requests"
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    submitter_name = models.CharField(max_length=200, blank=True)
    submitter_contact = models.CharField(max_length=200, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    target_service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_response = models.TextField(blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responded_requests",
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    requested_start_time = models.TimeField(null=True, blank=True)
    requested_end_time = models.TimeField(null=True, blank=True)
    approved_text = models.TextField(
        blank=True,
        help_text="The coordinator's reworded version, used to create the Announcement on approval.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status}] {self.title}"


class ServiceLog(models.Model):
    ACTION_CHOICES = [
        ("created", "Service Created"),
        ("item_added", "Item Added"),
        ("item_edited", "Item Edited"),
        ("item_completed", "Item Marked Complete"),
        ("time_shifted", "Times Shifted"),
        ("frozen", "Bulletin Frozen"),
        ("unfrozen", "Bulletin Unfrozen"),
        ("request_approved", "Request Approved"),
        ("request_rejected", "Request Rejected"),
    ]

    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True)
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True
    )
    service_item = models.ForeignKey(
        ServiceItem, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at} — {self.action}"


class Bulletin(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="bulletins")
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="bulletins", editable=False
    )
    version = models.PositiveIntegerField(default=1)
    snapshot_json = models.JSONField()
    frozen_at = models.DateTimeField(auto_now_add=True)
    frozen_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = [("service", "version")]
        ordering = ["-version"]

    def save(self, *args, **kwargs):
        self.church_id = self.service.church_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service.name} — v{self.version}"


class Announcement(models.Model):
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="announcements"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, null=True, blank=True, related_name="announcements"
    )
    body = models.TextField()
    is_paused = models.BooleanField(default=False)
    show_on_public = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "-created_at"]

    def __str__(self):
        return self.body[:60]

    def is_active_now(self):
        from django.utils import timezone
        today = timezone.localdate()
        return not self.is_paused and self.start_date <= today <= self.end_date

    def is_upcoming(self):
        from django.utils import timezone
        return self.start_date > timezone.localdate()

    def is_older(self):
        from django.utils import timezone
        return self.end_date < timezone.localdate()


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.title}"


class AIInsight(models.Model):
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="ai_insights"
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    period_start = models.DateField()
    period_end = models.DateField()
    content = models.TextField()
    raw_stats = models.JSONField()

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"AI Insight for {self.church.name} — {self.generated_at}"


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="settings"
    )
    notifications_enabled = models.BooleanField(default=True)
    theme_preference = models.CharField(max_length=10, default="light")

    def __str__(self):
        return f"Settings for {self.user.username}"


class ChurchEvent(models.Model):
    """An activity that is not a formal service, such as practice or outreach."""

    EVENT_TYPES = [
        ("rehearsal", "Rehearsal / Practice"),
        ("study", "Bible Study"),
        ("meeting", "Meeting"),
        ("outreach", "Outreach"),
        ("fellowship", "Fellowship"),
        ("other", "Other"),
    ]

    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="events"
    )
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200, blank=True)
    responsible_department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.title} — {self.date}"


class Resource(models.Model):
    """A bookable space or asset in a church."""
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="resources"
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    requires_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("church", "name")]
        ordering = ["name"]

    def __str__(self):
        return f"{self.church.name} — {self.name}"


class ResourceBooking(models.Model):
    """A request to use a resource for a period of time."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="bookings"
    )
    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, related_name="bookings"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    purpose = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="decided_bookings",
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return f"{self.resource.name} — {self.purpose} ({self.starts_at:%d %b %H:%M})"

    def has_conflict(self):
        """Return the first conflicting approved booking, if any."""
        others = ResourceBooking.objects.filter(
            resource=self.resource, status="approved"
        ).exclude(pk=self.pk)
        for other in others:
            if self.starts_at < other.ends_at and self.ends_at > other.starts_at:
                return other
        return None


class Invitation(models.Model):
    """A one-time invitation for a department head to join a church."""
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="invitations"
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=20, choices=Membership.ROLE_CHOICES, default="dept_head"
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    token = models.CharField(max_length=64, unique=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        from datetime import timedelta
        from django.utils import timezone
        if self.accepted_at:
            return False
        return timezone.now() - self.created_at < timedelta(days=7)

    def __str__(self):
        return f"Invitation for {self.email} to {self.church.name}"
