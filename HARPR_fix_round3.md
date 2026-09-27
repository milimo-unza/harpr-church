# Harpr — Round 3 fixes

**This file replaces two broken templates, adds week navigation to the
dashboard, rebuilds the seed data, upgrades the bulletin PDF, and
adds bulletin settings to the church settings page.**

Do not re-apply anything from earlier fix files.

---

## Before you start

**Environment:**

```
cd /root/harpr && . .venv/bin/activate
```

**Verification after each section:**

```
python manage.py check
python manage.py test church
```

---

## Section S1 — Fix `members.html`

Copilot appended new content on top of the old file, which is why
`{% csrf_token %}` renders as text and `m.role=='dept_head'` fails to
parse (no spaces around the operator).

### S1.1 Overwrite `church/templates/church/members.html`

Overwrite the file completely:

```
{% extends "church/base.html" %}
{% block title %}Members · Harpr{% endblock %}
{% block content %}
<div class="page-head">
  <div>
    <p class="eyebrow">Access</p>
    <h1>Members</h1>
  </div>
  <button type="button" class="btn btn-primary" data-modal-open="invite-modal">Add member</button>
</div>

<div class="card table-wrap">
  <table class="data-table">
    <thead>
      <tr>
        <th>Username</th>
        <th>Email</th>
        <th>Role</th>
        <th>Department</th>
        <th>Status</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {% for m in memberships %}
        <tr>
          <td>{{ m.user.username }}</td>
          <td>{{ m.user.email|default:"—" }}</td>
          <td>{{ m.get_role_display }}</td>
          <td>{{ m.department.name|default:"—" }}</td>
          <td>
            {% if m.is_active %}
              <span class="status-badge status-approved">Active</span>
            {% else %}
              <span class="status-badge status-skipped">Deactivated</span>
            {% endif %}
          </td>
          <td class="row-actions-inline">
            <button type="button" class="btn btn-small" data-modal-open="edit-member-{{ m.pk }}">Edit</button>
            {% if m.is_active %}
              <button type="button" class="btn btn-small btn-danger" data-modal-open="deactivate-member-{{ m.pk }}">Deactivate</button>
            {% else %}
              <button type="button" class="btn btn-small" data-modal-open="reactivate-member-{{ m.pk }}">Reactivate</button>
            {% endif %}
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="6" class="empty-state">No members yet.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<div class="modal-backdrop" id="invite-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true">
    <div class="modal-head">
      <h2>Invite member</h2>
      <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
    </div>
    <div class="modal-body">
      <p class="muted">Enter the person's email address and choose their role and department. Harpr will email them an invitation link that expires in 7 days and can only be used once.</p>
      <form method="post" action="{% url 'member_invite' %}">
        {% csrf_token %}
        <div class="form-row">
          <label for="invite_email">Email</label>
          <input type="email" name="email" id="invite_email" required>
        </div>
        <div class="form-row">
          <label for="invite_role">Role</label>
          <select name="role" id="invite_role">
            <option value="dept_head">Department Head</option>
            <option value="admin">Administrator</option>
          </select>
        </div>
        <div class="form-row">
          <label for="invite_department">Department</label>
          <select name="department" id="invite_department">
            <option value="">— None —</option>
            {% for d in departments %}
              <option value="{{ d.pk }}">{{ d.name }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-ghost modal-close">Cancel</button>
          <button type="submit" class="btn btn-primary">Send invitation</button>
        </div>
      </form>
    </div>
  </div>
</div>

{% for m in memberships %}
  <div class="modal-backdrop" id="edit-member-{{ m.pk }}" hidden>
    <div class="modal" role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>Edit {{ m.user.username }}</h2>
        <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
      </div>
      <div class="modal-body">
        <p class="muted">Names and emails are managed by the member themselves. As administrator you can change their role or department, or deactivate their account.</p>
        <form method="post" action="{% url 'member_edit' m.pk %}">
          {% csrf_token %}
          <div class="form-row">
            <label for="edit-role-{{ m.pk }}">Role</label>
            <select name="role" id="edit-role-{{ m.pk }}">
              <option value="dept_head" {% if m.role == 'dept_head' %}selected{% endif %}>Department Head</option>
              <option value="admin" {% if m.role == 'admin' %}selected{% endif %}>Administrator</option>
            </select>
          </div>
          <div class="form-row">
            <label for="edit-dept-{{ m.pk }}">Department</label>
            <select name="department" id="edit-dept-{{ m.pk }}">
              <option value="">— None —</option>
              {% for d in departments %}
                <option value="{{ d.pk }}" {% if m.department_id == d.pk %}selected{% endif %}>{{ d.name }}</option>
              {% endfor %}
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-ghost modal-close">Cancel</button>
            <button type="submit" class="btn btn-primary">Save changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <div class="modal-backdrop" id="deactivate-member-{{ m.pk }}" hidden>
    <div class="modal modal--narrow" role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>Deactivate member?</h2>
        <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
      </div>
      <div class="modal-body">
        <p>Deactivating <strong>{{ m.user.username }}</strong> will prevent them from signing in. They will receive a notification.</p>
        <form method="post" action="{% url 'member_deactivate' m.pk %}">
          {% csrf_token %}
          <div class="form-actions">
            <button type="button" class="btn btn-ghost modal-close">Cancel</button>
            <button type="submit" class="btn btn-danger">Deactivate</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <div class="modal-backdrop" id="reactivate-member-{{ m.pk }}" hidden>
    <div class="modal modal--narrow" role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>Reactivate member?</h2>
        <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
      </div>
      <div class="modal-body">
        <p>Enter your administrator password to reactivate <strong>{{ m.user.username }}</strong>. They will receive a notification.</p>
        <form method="post" action="{% url 'member_reactivate' m.pk %}">
          {% csrf_token %}
          <div class="form-row">
            <label for="admin-pwd-{{ m.pk }}">Your password</label>
            <input type="password" name="admin_password" id="admin-pwd-{{ m.pk }}" required autocomplete="current-password">
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-ghost modal-close">Cancel</button>
            <button type="submit" class="btn btn-primary">Reactivate</button>
          </div>
        </form>
      </div>
    </div>
  </div>
{% endfor %}

<script>
  (function () {
    document.querySelectorAll("[data-modal-open]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var el = document.getElementById(btn.getAttribute("data-modal-open"));
        if (el) el.hidden = false;
      });
    });
    document.querySelectorAll(".modal-backdrop").forEach(function (backdrop) {
      backdrop.addEventListener("click", function (e) {
        if (e.target === backdrop) backdrop.hidden = true;
      });
      backdrop.querySelectorAll(".modal-close").forEach(function (b) {
        b.addEventListener("click", function () { backdrop.hidden = true; });
      });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        document.querySelectorAll(".modal-backdrop").forEach(function (m) {
          m.hidden = true;
        });
      }
    });
  })();
</script>
{% endblock %}
```

### S1.2 Verify

```
python manage.py check
python manage.py test church
```

Visit `/members/`. All five buttons should work.

---

## Section S2 — Fix `announcements.html`

The file has duplicate content — the entire page is written twice. This
causes the `'block' tag with name 'title' appears more than once` error.

### S2.1 Overwrite `church/templates/church/announcements.html`

Overwrite the file completely:

```
{% extends "church/base.html" %}
{% block title %}Announcements · Harpr{% endblock %}
{% block content %}
<div class="page-head">
  <div>
    <p class="eyebrow">Public information</p>
    <h1>Announcements</h1>
  </div>
  <button type="button" class="btn btn-primary" data-modal-open="announcement-create-modal">New announcement</button>
</div>

<h2 class="section-label">Active</h2>
<div class="card table-wrap">
  <table class="data-table">
    <thead>
      <tr><th>Announcement</th><th>Runs</th><th>Public</th><th></th></tr>
    </thead>
    <tbody>
      {% for announcement in active_announcements %}
        <tr>
          <td>{{ announcement.body|truncatechars:80 }}</td>
          <td class="mono">{{ announcement.start_date|date:"d M" }} → {{ announcement.end_date|date:"d M Y" }}</td>
          <td>{{ announcement.show_on_public|yesno:"Yes,No" }}</td>
          <td class="row-actions-inline">
            <button type="button" class="btn btn-small" data-modal-open="announcement-edit-{{ announcement.pk }}">Edit</button>
            <form method="post" action="{% url 'announcement_pause' announcement.pk %}" class="inline-form">
              {% csrf_token %}
              <button class="btn btn-small" type="submit">{% if announcement.is_paused %}Resume{% else %}Pause{% endif %}</button>
            </form>
            <form method="post" action="{% url 'announcement_delete' announcement.pk %}" class="inline-form" onsubmit="return confirm('Delete this announcement?');">
              {% csrf_token %}
              <button class="btn btn-small btn-danger" type="submit">Delete</button>
            </form>
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="4" class="empty-state">Nothing active right now.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<h2 class="section-label">Upcoming</h2>
<div class="card table-wrap">
  <table class="data-table">
    <thead>
      <tr><th>Announcement</th><th>Starts</th><th></th></tr>
    </thead>
    <tbody>
      {% for announcement in upcoming_announcements %}
        <tr>
          <td>{{ announcement.body|truncatechars:80 }}</td>
          <td class="mono">{{ announcement.start_date|date:"d M Y" }}</td>
          <td class="row-actions-inline">
            <button type="button" class="btn btn-small" data-modal-open="announcement-edit-{{ announcement.pk }}">Edit</button>
            <form method="post" action="{% url 'announcement_delete' announcement.pk %}" class="inline-form" onsubmit="return confirm('Delete this announcement?');">
              {% csrf_token %}
              <button class="btn btn-small btn-danger" type="submit">Delete</button>
            </form>
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="3" class="empty-state">Nothing scheduled.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<h2 class="section-label">Older</h2>
<div class="card table-wrap">
  <table class="data-table">
    <thead>
      <tr><th>Announcement</th><th>Ran</th></tr>
    </thead>
    <tbody>
      {% for announcement in older_announcements %}
        <tr>
          <td>{{ announcement.body|truncatechars:80 }}</td>
          <td class="mono">{{ announcement.start_date|date:"d M" }} → {{ announcement.end_date|date:"d M Y" }}</td>
        </tr>
      {% empty %}
        <tr><td colspan="2" class="empty-state">No past announcements.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>

<div class="modal-backdrop" id="announcement-create-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true">
    <div class="modal-head">
      <h2>New announcement</h2>
      <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
    </div>
    <div class="modal-body">
      <form method="post" action="{% url 'announcement_create' %}">
        {% csrf_token %}
        <div class="form-row">
          <label for="new-ann-body">Announcement</label>
          <textarea name="body" id="new-ann-body" rows="4" required></textarea>
        </div>
        <div class="form-row two-up">
          <div>
            <label for="new-ann-start">Start date</label>
            <input type="date" name="start_date" id="new-ann-start" required>
          </div>
          <div>
            <label for="new-ann-end">End date</label>
            <input type="date" name="end_date" id="new-ann-end" required>
          </div>
        </div>
        <div class="form-row">
          <label class="checkbox-line">
            <input type="checkbox" name="show_on_public" checked>
            Show on the public bulletin
          </label>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-ghost modal-close">Cancel</button>
          <button type="submit" class="btn btn-primary">Create announcement</button>
        </div>
      </form>
    </div>
  </div>
</div>

{% for announcement in active_announcements %}
  <div class="modal-backdrop" id="announcement-edit-{{ announcement.pk }}" hidden>
    <div class="modal" role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>Edit announcement</h2>
        <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
      </div>
      <div class="modal-body">
        <form method="post" action="{% url 'announcement_edit' announcement.pk %}">
          {% csrf_token %}
          <div class="form-row">
            <label for="edit-ann-body-{{ announcement.pk }}">Announcement</label>
            <textarea name="body" id="edit-ann-body-{{ announcement.pk }}" rows="4" required>{{ announcement.body }}</textarea>
          </div>
          <div class="form-row two-up">
            <div>
              <label for="edit-ann-start-{{ announcement.pk }}">Start date</label>
              <input type="date" name="start_date" id="edit-ann-start-{{ announcement.pk }}" value="{{ announcement.start_date|date:'Y-m-d' }}" required>
            </div>
            <div>
              <label for="edit-ann-end-{{ announcement.pk }}">End date</label>
              <input type="date" name="end_date" id="edit-ann-end-{{ announcement.pk }}" value="{{ announcement.end_date|date:'Y-m-d' }}" required>
            </div>
          </div>
          <div class="form-row">
            <label class="checkbox-line">
              <input type="checkbox" name="show_on_public" {% if announcement.show_on_public %}checked{% endif %}>
              Show on the public bulletin
            </label>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-ghost modal-close">Cancel</button>
            <button type="submit" class="btn btn-primary">Save changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
{% endfor %}

{% for announcement in upcoming_announcements %}
  <div class="modal-backdrop" id="announcement-edit-{{ announcement.pk }}" hidden>
    <div class="modal" role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>Edit announcement</h2>
        <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
      </div>
      <div class="modal-body">
        <form method="post" action="{% url 'announcement_edit' announcement.pk %}">
          {% csrf_token %}
          <div class="form-row">
            <label for="up-edit-ann-body-{{ announcement.pk }}">Announcement</label>
            <textarea name="body" id="up-edit-ann-body-{{ announcement.pk }}" rows="4" required>{{ announcement.body }}</textarea>
          </div>
          <div class="form-row two-up">
            <div>
              <label for="up-edit-ann-start-{{ announcement.pk }}">Start date</label>
              <input type="date" name="start_date" id="up-edit-ann-start-{{ announcement.pk }}" value="{{ announcement.start_date|date:'Y-m-d' }}" required>
            </div>
            <div>
              <label for="up-edit-ann-end-{{ announcement.pk }}">End date</label>
              <input type="date" name="end_date" id="up-edit-ann-end-{{ announcement.pk }}" value="{{ announcement.end_date|date:'Y-m-d' }}" required>
            </div>
          </div>
          <div class="form-row">
            <label class="checkbox-line">
              <input type="checkbox" name="show_on_public" {% if announcement.show_on_public %}checked{% endif %}>
              Show on the public bulletin
            </label>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-ghost modal-close">Cancel</button>
            <button type="submit" class="btn btn-primary">Save changes</button>
          </div>
        </form>
      </div>
    </div>
  </div>
{% endfor %}

<script>
  (function () {
    document.querySelectorAll("[data-modal-open]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var el = document.getElementById(btn.getAttribute("data-modal-open"));
        if (el) el.hidden = false;
      });
    });
    document.querySelectorAll(".modal-backdrop").forEach(function (backdrop) {
      backdrop.addEventListener("click", function (e) {
        if (e.target === backdrop) backdrop.hidden = true;
      });
      backdrop.querySelectorAll(".modal-close").forEach(function (b) {
        b.addEventListener("click", function () { backdrop.hidden = true; });
      });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        document.querySelectorAll(".modal-backdrop").forEach(function (m) {
          m.hidden = true;
        });
      }
    });
  })();
</script>
{% endblock %}
```

### S2.2 Verify

```
python manage.py check
python manage.py test church
```

Visit `/announcements/`. The page loads. "New announcement" opens a modal.

---

## Section S3 — Add week navigation to the dashboard

The coordinator needs Previous / Today / Next buttons to see past and
future weeks.

### S3.1 Update `admin_dashboard` view

In `church/views/admin_views.py`, replace `admin_dashboard` with:

```
@admin_required
def admin_dashboard(request):
    from datetime import date, timedelta

    today = timezone.localdate()
    week_param = request.GET.get("week")

    if week_param:
        try:
            ref = date.fromisoformat(week_param)
        except ValueError:
            ref = today
    else:
        ref = today

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

    return render(request, "church/dashboard.html", {
        "church": request.church,
        "today": today,
        "week_start": week_start,
        "week_end": week_end,
        "prev_week": prev_week,
        "next_week": next_week,
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
        "service_templates": request.church.service_templates.filter(is_active=True),
    })
```

### S3.2 Update the dashboard header

In `church/templates/church/dashboard.html`, find the page-head block and
replace the `<p class="muted">` line with the navigation:

```
    <p class="muted">{{ week_start|date:"d M" }} — {{ week_end|date:"d M Y" }}</p>
```

Replace with:

```
    <div class="week-nav">
      <a class="btn btn-small" href="?week={{ prev_week|date:'Y-m-d' }}">← Previous</a>
      <a class="btn btn-small" href="{% url 'admin_dashboard' %}">Today</a>
      <a class="btn btn-small" href="?week={{ next_week|date:'Y-m-d' }}">Next →</a>
      <span class="muted" style="margin-left:8px;">{{ week_start|date:"d M" }} — {{ week_end|date:"d M Y" }}</span>
    </div>
```

### S3.3 Verify

Visit `/dashboard/`. You should see Previous / Today / Next buttons.
Click Next — the week grid moves forward. Click Today — returns to
the current week.

---

## Section S4 — Rebuild the seed data

Copilot needs to run a command that generates demo data from July
through November 2026, including completed services so the AI
Insights page has data.

### S4.1 Replace `church/management/commands/seed_demo.py`

Overwrite the file completely:

```
from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from church.models import (
    Announcement,
    Assignment,
    Church,
    ChurchEvent,
    Department,
    Membership,
    Person,
    Service,
    ServiceItem,
    ServiceItemTemplate,
    ServiceLog,
    ServiceTemplate,
)

User = get_user_model()

class Command(BaseCommand):
    help = "Rebuild the Harpr Church demonstration data."

    def handle(self, *args, **options):
        today = timezone.localdate()

        church, _ = Church.objects.update_or_create(
            slug="grace-covenant",
            defaults={
                "name": "Grace Covenant Church",
                "timezone": "Africa/Lusaka",
                "address": "Lusaka, Zambia",
                "contact_phone": "+260 211 123 456",
                "contact_email": "office@gracecovenant.org.zm",
                "contact_whatsapp": "260971234567",
                "footer_verse": "The Lord bless you and keep you. — Numbers 6:24",
                "is_active": True,
            },
        )

        departments = {}
        for slug, name, color in [
            ("pastors", "Pastors", "#a85430"),
            ("music", "Music", "#4a7d57"),
            ("ushering", "Ushering", "#5a7ba0"),
            ("media", "Media", "#7865a0"),
            ("children", "Children", "#b58a30"),
            ("prayer", "Prayer", "#4a7a7c"),
        ]:
            departments[slug], _ = Department.objects.update_or_create(
                church=church,
                slug=slug,
                defaults={"name": name, "color": color},
            )

        coordinator = self._user("coordinator", "coordinator@example.com",
                                 "Programme", "Coordinator")
        Membership.objects.update_or_create(
            user=coordinator, church=church,
            defaults={"role": "admin", "department": None, "is_active": True},
        )

        heads = {
            "music_head": ("music", "Music"),
            "pastors_head": ("pastors", "Pastors"),
            "ushering_head": ("ushering", "Ushering"),
            "media_head": ("media", "Media"),
        }
        for username, (dept_slug, title) in heads.items():
            user = self._user(username, f"{username}@example.com", title, "Head")
            Membership.objects.update_or_create(
                user=user, church=church,
                defaults={
                    "role": "dept_head",
                    "department": departments[dept_slug],
                    "is_active": True,
                },
            )

        # Template
        template, _ = ServiceTemplate.objects.update_or_create(
            church=church,
            name="Sunday Worship Service",
            defaults={
                "day_of_week": 6,
                "default_start_time": time(8, 0),
                "default_duration_minutes": 120,
                "is_active": True,
            },
        )
        item_specs = [
            ("Pre-Service Music", 10, "music"),
            ("Call to Worship", 5, "pastors"),
            ("Opening Prayer", 10, "prayer"),
            ("Worship Songs", 25, "music"),
            ("Scripture Reading", 5, "pastors"),
            ("Sermon", 45, "pastors"),
            ("Response Song", 10, "music"),
            ("Announcements", 10, "pastors"),
            ("Offering", 10, "ushering"),
            ("Benediction", 5, "pastors"),
        ]
        for order, (title, duration, dept_slug) in enumerate(item_specs):
            ServiceItemTemplate.objects.update_or_create(
                template=template, order=order,
                defaults={
                    "title": title,
                    "default_duration_minutes": duration,
                    "responsible_department": departments[dept_slug],
                },
            )

        # Services: July 5 to November 29 2026
        anchor = date(2026, 7, 5)
        end = date(2026, 11, 29)
        service_dates = []
        cursor = anchor
        while cursor <= end:
            service_dates.append(cursor)
            cursor += timedelta(days=7)

        Service.objects.filter(church=church).delete()

        names = {
            "Sermon": ["Pastor Phiri", "Pastor Banda", "Pastor Mulenga"],
            "Worship Songs": ["Ruth Mwansa", "Mwaka Zulu", "Chanda Tembo"],
            "Offering": ["Moses Lungu", "Esther Chileshe", "Andrew Sakala"],
            "Scripture Reading": ["Grace Mumba", "Brian Kunda", "Naomi Sampa"],
        }

        for idx, service_date in enumerate(service_dates):
            is_past = service_date < today
            service, _ = Service.objects.update_or_create(
                church=church, date=service_date, name="Sunday Worship Service",
                defaults={
                    "template": template,
                    "status": "completed" if is_past else "draft",
                },
            )
            start = timezone.make_aware(datetime.combine(service_date, time(8, 0)))
            for order, (title, duration, dept_slug) in enumerate(item_specs):
                actual_start = start if is_past else None
                actual_duration = duration if is_past else None
                item, _ = ServiceItem.objects.update_or_create(
                    service=service, order=order,
                    defaults={
                        "title": title,
                        "planned_start": start,
                        "planned_duration_minutes": duration,
                        "actual_start": actual_start,
                        "actual_duration_minutes": actual_duration,
                        "status": "completed" if is_past else "planned",
                        "responsible_department": departments[dept_slug],
                    },
                )
                if title in names:
                    Assignment.objects.update_or_create(
                        service_item=item,
                        person_name=names[title][idx % len(names[title])],
                        role=title,
                        defaults={"church": church},
                    )
                start += timedelta(minutes=duration)

        # Events: spread across the period
        ChurchEvent.objects.filter(church=church).delete()
        event_templates = [
            ("Choir Practice", "rehearsal", 2, time(18, 0), time(19, 30), "music"),
            ("Bible Study", "study", 4, time(18, 30), time(20, 0), "pastors"),
            ("Youth Meeting", "meeting", 5, time(14, 0), time(16, 0), "children"),
            ("Prayer Meeting", "meeting", 5, time(9, 0), time(11, 0), "prayer"),
            ("Media Team Rehearsal", "rehearsal", 1, time(17, 0), time(18, 0), "media"),
        ]
        for week_offset in range(0, 22, 2):
            week_start = anchor + timedelta(weeks=week_offset)
            for title, event_type, day_offset, start_time, end_time, dept_slug in event_templates:
                ChurchEvent.objects.create(
                    church=church, title=title, event_type=event_type,
                    date=week_start + timedelta(days=day_offset),
                    start_time=start_time, end_time=end_time,
                    location="Main church campus",
                    responsible_department=departments[dept_slug],
                )

        # Announcements
        Announcement.objects.filter(church=church).delete()
        announcements = [
            ("Mid-week prayer meeting moves to Wednesday at 18:00. All are welcome.",
             today - timedelta(days=60), today - timedelta(days=30)),
            ("The choir is recruiting new members. Speak to the music department.",
             today - timedelta(days=45), today - timedelta(days=15)),
            ("Monthly outreach to Matero is this Saturday at 09:00. Meet at the car park.",
             today - timedelta(days=7), today + timedelta(days=7)),
            ("Harvest thanksgiving service is on the last Sunday of October.",
             today - timedelta(days=2), today + timedelta(days=20)),
            ("Youth camp registration closes at the end of the month.",
             today + timedelta(days=5), today + timedelta(days=40)),
            ("New believers' class begins next month. Sign up with the pastors' department.",
             today + timedelta(days=14), today + timedelta(days=60)),
        ]
        for body, start_date, end_date in announcements:
            Announcement.objects.create(
                church=church, body=body,
                start_date=start_date, end_date=end_date,
                is_paused=False, show_on_public=True,
            )

        # Service logs so the dashboard shows recent activity
        ServiceLog.objects.filter(church=church).delete()
        recent_service = Service.objects.filter(church=church, date__lt=today).order_by("-date").first()
        if recent_service:
            ServiceLog.objects.create(
                church=church, user=coordinator, service=recent_service,
                action="frozen", details="Bulletin frozen for Sunday.",
            )
            ServiceLog.objects.create(
                church=church, user=coordinator, service=recent_service,
                action="completed", details="Service marked complete.",
            )

        self.stdout.write(self.style.SUCCESS("Harpr demo data rebuilt."))
        self.stdout.write("Coordinator: coordinator / harpr2026")
        self.stdout.write("Public URL: /c/grace-covenant/")

    @staticmethod
    def _user(username, email, first_name, last_name):
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": first_name, "last_name": last_name},
        )
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.set_password("harpr2026")
        user.save()
        return user
```

### S4.2 Run it

```
python manage.py seed_demo
```

You should see "Harpr demo data rebuilt."

Then visit `/dashboard/` — services from July through November should appear.
Navigate forward and back with the new buttons.

Visit `/ai-insights/` — with 12 completed services now in the database,
the AI should be able to generate insights instead of saying "not enough
data."

### S4.3 Verify

```
python manage.py check
```