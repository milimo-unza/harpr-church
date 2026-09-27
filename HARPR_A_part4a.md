# Harpr — MD A, Part 4a: Model cleanup, PDF, announcement and service modals

**This is part 4a of 4b.** Parts 1, 2, 2b, and 3 are already applied.

- **Part 4a (this file):** Sections P4.1 → P4.6
- Part 4b: Sections P4.7 → P4.10

**Read this entire file before touching code. Do not read part 4b until told to.**

---

## Before you start

**Repo state:** all of parts 1–3 are applied. `git status` shows
22 modified files, several new files, and 4 `.Zone.Identifier` junk
files. Nothing is committed yet. `origin/main` is at `165c305`.

**Environment:**

```
cd /root/harpr && . .venv/bin/activate
```

Use `python` after activating the venv.

**Verification after each section:**

```
python manage.py check
python manage.py test church
```

Both must pass before continuing.

---

## Section P4.1 — Fix `Announcement.__str__`

In `church/models.py`, inside the `Announcement` class, find:

```
    def __str__(self):
        return self.title
```

Replace with:

```
    def __str__(self):
        return self.body[:60]
```

Run the two verification commands.

---

## Section P4.2 — Tighten the Announcement model

### P4.2.1 Edit the model

In `church/models.py`, replace the entire `Announcement` class with:

```
class Announcement(models.Model):
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name="announcements"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, null=True, blank=True,
        related_name="announcements",
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
```

Changes from the current version:

- Removed `title`
- Removed `is_active`
- Removed `expires_at`
- Changed `start_date` from `DateField(null=True, blank=True)` to `DateField()`
- Changed `end_date` from `DateField(null=True, blank=True)` to `DateField()`
- Changed `Meta.ordering` from `["-created_at"]` to `["-start_date", "-created_at"]`

### P4.2.2 Create the migration

Run:

```
python manage.py makemigrations church --name announcement_tighten
```

Django will prompt because existing rows may have null dates and you are
making the columns required. When prompted:

- For the change to `start_date`, choose **"Provide a one-off default now"** and enter:

```
django.utils.timezone.now
```
- For the change to `end_date`, choose the same and enter:

```
django.utils.timezone.now
```

Django will not prompt about removing `title`, `is_active`, or
`expires_at` — those are just drops.

### P4.2.3 Add a backfill step to the migration

Open the generated migration file
(`church/migrations/0007_announcement_tighten.py` or whichever number
Django assigned). Add these imports at the top:

```
from datetime import timedelta
from django.utils import timezone
```

Above the `Migration` class, add:

```
def backfill_announcement_dates(apps, schema_editor):
    """Give any null-dated announcements a reasonable window."""
    Announcement = apps.get_model("church", "Announcement")
    today = timezone.localdate()
    for announcement in Announcement.objects.all():
        changed = False
        if announcement.start_date is None:
            announcement.start_date = today
            changed = True
        if announcement.end_date is None:
            announcement.end_date = today + timedelta(days=30)
            changed = True
        if changed:
            announcement.save()
```

Inside the `operations` list, add this as the **very first** operation:

```
        migrations.RunPython(
            backfill_announcement_dates, migrations.RunPython.noop
        ),
```

### P4.2.4 Apply the migration

```
python manage.py migrate
```

### P4.2.5 Verify

```
python manage.py check
python manage.py test church
python manage.py makemigrations --check --dry-run
```

The third command must print "No changes detected."

### P4.2.6 Check for stragglers

Run:

```
grep -rn "\.title\b" church/ --include="*.py" --include="*.html" | grep -i announce
grep -rn "announcement.is_active" church/ --include="*.py" --include="*.html"
grep -rn "announcement.expires_at" church/ --include="*.py" --include="*.html"
```

If any return results, fix them.

Check `AnnouncementForm` in `church/forms.py`. Its `Meta.fields` must be exactly:

```
        fields = [
            "body",
            "service",
            "show_on_public",
            "start_date",
            "end_date",
            "is_paused",
        ]
```

Check `seed_demo.py` — no references to `title`, `is_active`, or
`expires_at`.

### P4.2.7 Rebuild the demo data

```
python manage.py seed_demo
```

Run the three verification commands one more time.

---

## Section P4.3 — Apply the PDF change (announcements on page 2)

### P4.3.1 Update the imports

Open `church/services/pdf.py`. Find:

```
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
```

Replace with:

```
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
```

### P4.3.2 Replace the announcements block

Find the announcements block near the bottom of `generate_bulletin_pdf`.
It currently reads something like:

```
    announcements = service.announcements.filter(is_active=True, show_on_public=True)
    if announcements:
        elements.append(Spacer(1, 12 * mm))
        elements.append(Paragraph("Announcements", title))
        for announcement in announcements:
            elements.append(
                Paragraph(
                    f"• {escape(announcement.title)}: {escape(announcement.body)}",
                    item_meta,
                )
            )
```

Replace that whole block with:

```
    from django.utils import timezone
    today = timezone.localdate()

    announcements = service.church.announcements.filter(
        is_paused=False,
        show_on_public=True,
        start_date__lte=today,
        end_date__gte=today,
    ).order_by("start_date")

    if announcements.exists():
        elements.append(PageBreak())
        elements.append(Paragraph("Announcements", title))
        for announcement in announcements:
            elements.append(
                Paragraph(
                    f"• {escape(announcement.body)}",
                    item_meta,
                )
            )
```

### P4.3.3 Verify

Run the two verification commands. Then start the dev server, visit
`/c/grace-covenant/`, click "Download PDF", and confirm the
announcements appear on page 2.

---

## Section P4.4 — Add the announcement create and edit modals

### P4.4.1 Replace `church/templates/church/announcements.html`

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
      <tr>
        <th>Announcement</th>
        <th>Runs</th>
        <th>Public</th>
        <th></th>
      </tr>
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

{# ---------- Create modal ---------- #}
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
          <label for="new-ann-service">Service (optional)</label>
          <select name="service" id="new-ann-service">
            <option value="">— All programmes —</option>
            {% for s in services %}
              <option value="{{ s.pk }}">{{ s.name }} — {{ s.date|date:"d M Y" }}</option>
            {% endfor %}
          </select>
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

{# ---------- Edit modals ---------- #}
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
            <label for="edit-ann-service-{{ announcement.pk }}">Service (optional)</label>
            <select name="service" id="edit-ann-service-{{ announcement.pk }}">
              <option value="">— All programmes —</option>
              {% for s in services %}
                <option value="{{ s.pk }}" {% if announcement.service_id == s.pk %}selected{% endif %}>{{ s.name }} — {{ s.date|date:"d M Y" }}</option>
              {% endfor %}
            </select>
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
            <label for="up-edit-ann-service-{{ announcement.pk }}">Service (optional)</label>
            <select name="service" id="up-edit-ann-service-{{ announcement.pk }}">
              <option value="">— All programmes —</option>
              {% for s in services %}
                <option value="{{ s.pk }}" {% if announcement.service_id == s.pk %}selected{% endif %}>{{ s.name }} — {{ s.date|date:"d M Y" }}</option>
              {% endfor %}
            </select>
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

### P4.4.2 Update `announcement_list` view to pass services

Replace `announcement_list` in `church/views/admin_views.py` with:

```
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

    services = request.church.services.filter(
        date__gte=today - timedelta(days=30)
    ).order_by("date")[:60]

    return render(request, "church/announcements.html", {
        "active_announcements": active,
        "upcoming_announcements": upcoming,
        "older_announcements": older,
        "services": services,
    })
```

Run the two verification commands. Then visit `/announcements/` and
click "New announcement" — a modal should open. Fill it in, submit, and
the new announcement should appear in the appropriate section.

---

## Section P4.5 — Convert New Service to a modal

### P4.5.1 Pass `service_templates` to the dashboard

In `church/views/admin_views.py`, inside `admin_dashboard`, find the
`return render(...)` call. Add this key to the context dict:

```
            "service_templates": request.church.service_templates.filter(is_active=True),
```

Place it right after the existing `"days": days,` line.

### P4.5.2 Replace `church/templates/church/dashboard.html`

Overwrite the file completely:

```
{% extends "church/base.html" %}
{% block title %}Weekly programme · Harpr{% endblock %}
{% block content %}
<div class="page-head">
  <div>
    <p class="eyebrow">{{ church.name }} · Programme Coordinator</p>
    <h1>Weekly programme</h1>
    <p class="muted">{{ week_start|date:"d M" }} — {{ week_end|date:"d M Y" }}</p>
  </div>
  <div class="button-row">
    <button type="button" class="btn btn-primary" data-modal-open="event-create-modal">New event</button>
    <button type="button" class="btn btn-ghost" data-modal-open="service-create-modal">New service</button>
  </div>
</div>

<section class="stat-grid">
  <div class="stat-card"><strong>{{ service_count }}</strong><span>Services this month</span></div>
  <div class="stat-card"><strong>{{ pending_request_count }}</strong><span>Pending requests</span></div>
  <div class="stat-card"><strong>{{ recent_activity|length }}</strong><span>Recent actions</span></div>
</section>

<section class="week-grid" aria-label="Weekly calendar">
  {% for day in days %}
    <article class="week-col {% if day.date == today %}today{% endif %}">
      <header class="week-col-head">
        <strong>{{ day.date|date:"D" }}</strong>
        <small>{{ day.date|date:"d M" }}</small>
      </header>
      <div class="week-col-body">
        {% for service in day.services %}
          <a class="event-chip service-chip" href="{% url 'service_detail' service.pk %}">
            <strong>{{ service.name }}</strong>
            <small>Service · {{ service.get_status_display }}</small>
          </a>
        {% endfor %}
        {% for event in day.events %}
          <a class="event-chip" href="{% url 'event_edit' event.pk %}">
            <strong>{{ event.title }}</strong>
            <small>{{ event.get_event_type_display }} · {{ event.start_time|time:"H:i" }}</small>
          </a>
        {% endfor %}
        {% if not day.services and not day.events %}
          <span class="empty-day">Nothing scheduled</span>
        {% endif %}
      </div>
    </article>
  {% endfor %}
</section>

{# ---------- New event modal ---------- #}
<div class="modal-backdrop" id="event-create-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true">
    <div class="modal-head">
      <h2>New event</h2>
      <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
    </div>
    <div class="modal-body">
      <form method="post" action="{% url 'event_create' %}">
        {% csrf_token %}
        <div class="form-row">
          <label for="event-title">Title</label>
          <input name="title" id="event-title" required>
        </div>
        <div class="form-row">
          <label for="event-type">Type</label>
          <select name="event_type" id="event-type">
            <option value="rehearsal">Rehearsal / Practice</option>
            <option value="study">Bible Study</option>
            <option value="meeting">Meeting</option>
            <option value="outreach">Outreach</option>
            <option value="fellowship">Fellowship</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div class="form-row">
          <label for="event-date">Date</label>
          <input type="date" name="date" id="event-date" required>
        </div>
        <div class="form-row two-up">
          <div>
            <label for="event-start">Start time</label>
            <input type="time" name="start_time" id="event-start" required>
          </div>
          <div>
            <label for="event-end">End time</label>
            <input type="time" name="end_time" id="event-end" required>
          </div>
        </div>
        <div class="form-row">
          <label for="event-location">Location</label>
          <input name="location" id="event-location">
        </div>
        <div class="form-row">
          <label for="event-dept">Responsible department</label>
          <select name="responsible_department" id="event-dept">
            <option value="">— None —</option>
            {% for d in church.departments.all %}
              <option value="{{ d.pk }}">{{ d.name }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="form-row">
          <label for="event-notes">Notes</label>
          <textarea name="notes" id="event-notes" rows="3"></textarea>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-ghost modal-close">Cancel</button>
          <button type="submit" class="btn btn-primary">Create event</button>
        </div>
      </form>
    </div>
  </div>
</div>

{# ---------- New service modal ---------- #}
<div class="modal-backdrop" id="service-create-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true">
    <div class="modal-head">
      <h2>New service</h2>
      <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
    </div>
    <div class="modal-body">
      <p class="muted">Choose a template to auto-generate the service items, or leave it blank to start empty.</p>
      <form method="post" action="{% url 'service_create' %}">
        {% csrf_token %}
        <div class="form-row">
          <label for="svc-name">Service name</label>
          <input name="name" id="svc-name" required>
        </div>
        <div class="form-row">
          <label for="svc-date">Date</label>
          <input type="date" name="date" id="svc-date" required>
        </div>
        <div class="form-row">
          <label for="svc-template">Template</label>
          <select name="template" id="svc-template">
            <option value="">— No template —</option>
            {% for t in service_templates %}
              <option value="{{ t.pk }}">{{ t.name }} ({{ t.get_day_of_week_display }})</option>
            {% endfor %}
          </select>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-ghost modal-close">Cancel</button>
          <button type="submit" class="btn btn-primary">Create service</button>
        </div>
      </form>
    </div>
  </div>
</div>

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

### P4.5.3 Redirect `service_create` to the dashboard on success

In `church/views/admin_views.py`, inside `service_create`, find:

```
        return redirect("service_list")
```

Replace with:

```
        return redirect("admin_dashboard")
```

Run the two verification commands. Then visit `/dashboard/` and click
"New service" — a modal should open.

---

## Section P4.6 — Add `deactivated_at` and 30-day hiding

### P4.6.1 Add the field to `Membership`

In `church/models.py`, inside the `Membership` class, find:

```
    is_active = models.BooleanField(default=True)
```

Add this line right after it:

```
    deactivated_at = models.DateTimeField(null=True, blank=True)
```

### P4.6.2 Create and apply the migration

```
python manage.py makemigrations church --name membership_deactivated_at
python manage.py migrate
```

`deactivated_at` is nullable so Django will not prompt for a default.

### P4.6.3 Update `member_deactivate` and `member_reactivate`

In `church/views/admin_views.py`, replace `member_deactivate` with:

```
@admin_required
@require_POST
def member_deactivate(request, pk):
    membership = get_object_or_404(request.church.memberships, pk=pk)
    membership.is_active = False
    membership.deactivated_at = timezone.now()
    membership.save(update_fields=["is_active", "deactivated_at"])

    notify_user(
        membership.user,
        "Your account has been deactivated",
        f"Your access to {request.church.name} has been suspended by an administrator.",
        church=request.church,
    )
    messages.success(request, f"{membership.user.username} deactivated.")
    return redirect("member_list")
```

Replace `member_reactivate` with:

```
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
    membership.deactivated_at = None
    membership.save(update_fields=["is_active", "deactivated_at"])

    notify_user(
        membership.user,
        "Your account has been reactivated",
        f"Your access to {request.church.name} has been restored.",
        church=request.church,
    )
    messages.success(request, f"{membership.user.username} reactivated.")
    return redirect("member_list")
```

### P4.6.4 Update `member_list`

Replace `member_list` in `church/views/admin_views.py` with:

```
@admin_required
def member_list(request):
    from django.db.models import Q

    show_all = request.GET.get("show") == "all"
    cutoff = timezone.now() - timedelta(days=30)

    base = request.church.memberships.select_related(
        "user", "department", "invited_by"
    )

    if not show_all:
        base = base.filter(
            Q(is_active=True)
            | Q(deactivated_at__isnull=True)
            | Q(deactivated_at__gte=cutoff)
        )

    memberships = base.order_by("is_active", "user__username")
    departments = request.church.departments.all()

    return render(request, "church/members.html", {
        "memberships": memberships,
        "departments": departments,
        "show_all": show_all,
    })
```

### P4.6.5 Add the "Show all members" toggle to `members.html`

In `church/templates/church/members.html`, find the page head:

```
<div class="page-head">
  <div>
    <p class="eyebrow">Access</p>
    <h1>Members</h1>
  </div>
  <button type="button" class="btn btn-primary" data-modal-open="invite-modal">Add member</button>
</div>
```

Replace with:

```
<div class="page-head">
  <div>
    <p class="eyebrow">Access</p>
    <h1>Members</h1>
    {% if show_all %}
      <p class="muted">Showing all members, including those deactivated more than 30 days ago.</p>
    {% endif %}
  </div>
  <div class="button-row">
    {% if show_all %}
      <a class="btn btn-ghost" href="{% url 'member_list' %}">Hide long-inactive</a>
    {% else %}
      <a class="btn btn-ghost" href="{% url 'member_list' %}?show=all">Show all members</a>
    {% endif %}
    <button type="button" class="btn btn-primary" data-modal-open="invite-modal">Add member</button>
  </div>
</div>
```

### P4.6.6 Verify `timedelta` is imported

At the top of `church/views/admin_views.py`, ensure:

```
from datetime import datetime, timedelta
```

is present. If only `datetime` is imported, add `timedelta`.

### P4.6.7 Test

Run the two verification commands. Then:

1. Visit `/members/` — all members visible.
2. Deactivate one — it moves to the bottom of the list.
3. Visit `/members/` again — the deactivated member is still visible.
4. Backdate it in a shell:

```
python manage.py shell
```

Then:

```
from django.utils import timezone
from datetime import timedelta
from church.models import Membership
m = Membership.objects.filter(is_active=False).first()
if m:
    m.deactivated_at = timezone.now() - timedelta(days=31)
    m.save(update_fields=["deactivated_at"])
    print("Backdated", m.user.username)
```

Reload `/members/`. The member should be gone. Click "Show all members"
— the member reappears.

**STOP. Do not read part 4b until instructed.**

---

## End of part 4a

Report completion status with:

- Output of `python manage.py check`
- Output of `python manage.py test church`
- Output of `python manage.py makemigrations --check --dry-run`
- Confirmation that the PDF renders announcements on page 2
- Confirmation that "New announcement" opens a modal
- Confirmation that "New service" opens a modal
- Confirmation that the "Show all members" toggle reveals backdated deactivated members

proceed to part 4b.