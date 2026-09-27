# Harpr — Round 2 fixes

**This file replaces `members.html`, fixes the dashboard service modal,
converts the department form to a modal, removes the Service dropdown
from the announcement create modal, and turns the notification bell
into a floating button.**

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

## Section R1 — Remove "Show all members" from the members view

### R1.1 Update `member_list` in `church/views/admin_views.py`

Replace the entire `member_list` function with:

```
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
```

This removes the `Q` import and the `show_all` logic entirely — all
members are shown, sorted with active ones first.

Run the two verification commands.

---

## Section R2 — Replace `church/templates/church/members.html`

The current template has two bugs: the CSRF token renders as literal
text (because the `{% csrf_token %}` tag is inside the wrong HTML
context) and the "Add member" button has no modal to open. This
section replaces the whole file.

### R2.1 Overwrite the file

Overwrite `church/templates/church/members.html` completely:

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

{# ---------- Invite modal ---------- #}
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

{# ---------- Per-member modals ---------- #}
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
        <p>Deactivating <strong>{{ m.user.username }}</strong> will prevent them from signing in. They will receive a notification. Their historical entries remain in the system.</p>
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

### R2.2 Verify

```
python manage.py check
python manage.py test church
```

Then visit `/members/` and confirm:

1. **No "Show all members" button** — only "Add member" appears on the right.
2. **No literal `{% csrf_token %}`** in the table cells.
3. **Click "Add member"** — invite modal opens.
4. **Click "Edit"** on any row — edit modal opens.
5. **Click "Deactivate"** — confirm modal opens.

If all five pass, R2 is complete.

---

## Section R3 — Fix "New service" on the dashboard

The dashboard's "New service" button opens `service-create-modal`, but
that modal was likely never added, or the dashboard's `admin_dashboard`
view doesn't pass `service_templates`. Let me fix both.

### R3.1 Ensure the dashboard view passes templates

In `church/views/admin_views.py`, find `admin_dashboard`. Its
`return render(...)` context should include:

```
            "service_templates": request.church.service_templates.filter(is_active=True),
```

If it's missing, add it.

### R3.2 Replace `church/templates/church/dashboard.html`

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
      <p class="muted">Choose a template to auto-generate the service items, or leave blank to start empty.</p>
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

### R3.3 Verify

Visit `/dashboard/`, click "New service". A modal should open with Name,
Date, and Template dropdown. If it does, R3 is complete.

---

## Section R4 — Convert New Department to a modal

### R4.1 Replace `church/templates/church/departments.html`

The Departments page currently has a link to `/departments/new/`. Change
it to open a modal on the same page.

Overwrite the file completely:

```
{% extends "church/base.html" %}
{% block title %}Departments · Harpr{% endblock %}
{% block content %}
<div class="page-head">
  <div>
    <p class="eyebrow">People and teams</p>
    <h1>Departments</h1>
  </div>
  <button type="button" class="btn btn-primary" data-modal-open="department-create-modal">New department</button>
</div>

<div class="card table-wrap">
  <table class="data-table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Slug</th>
        <th>Members</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {% for department in departments %}
        <tr>
          <td>{{ department.name }}</td>
          <td class="mono">{{ department.slug }}</td>
          <td>{{ department.membership_set.count }}</td>
          <td class="row-actions-inline">
            <button type="button" class="btn btn-small" data-modal-open="department-edit-{{ department.pk }}">Edit</button>
            <form method="post" action="{% url 'department_delete' department.pk %}" class="inline-form" onsubmit="return confirm('Delete this department? Members assigned to it will be unassigned.');">
              {% csrf_token %}
              <button class="btn btn-small btn-danger" type="submit">Delete</button>
            </form>
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="4" class="empty-state">No departments.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>

{# ---------- Create modal ---------- #}
<div class="modal-backdrop" id="department-create-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true">
    <div class="modal-head">
      <h2>New department</h2>
      <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
    </div>
    <div class="modal-body">
      <form method="post" action="{% url 'department_create' %}">
        {% csrf_token %}
        <div class="form-row">
          <label for="new-dept-name">Name</label>
          <input name="name" id="new-dept-name" required>
        </div>
        <div class="form-row">
          <label for="new-dept-slug">Slug</label>
          <input name="slug" id="new-dept-slug" required placeholder="e.g. worship">
          <small class="muted">Short identifier, lowercase, hyphens instead of spaces.</small>
        </div>
        <div class="form-row">
          <label for="new-dept-description">Description</label>
          <textarea name="description" id="new-dept-description" rows="3"></textarea>
        </div>
        <div class="form-row">
          <label for="new-dept-color">Colour</label>
          <input type="color" name="color" id="new-dept-color" value="#a85430">
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-ghost modal-close">Cancel</button>
          <button type="submit" class="btn btn-primary">Create department</button>
        </div>
      </form>
    </div>
  </div>
</div>

{# ---------- Edit modals ---------- #}
{% for department in departments %}
  <div class="modal-backdrop" id="department-edit-{{ department.pk }}" hidden>
    <div class="modal" role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>Edit {{ department.name }}</h2>
        <button type="button" class="icon-btn modal-close" aria-label="Close">✕</button>
      </div>
      <div class="modal-body">
        <form method="post" action="{% url 'department_edit' department.pk %}">
          {% csrf_token %}
          <div class="form-row">
            <label for="edit-dept-name-{{ department.pk }}">Name</label>
            <input name="name" id="edit-dept-name-{{ department.pk }}" value="{{ department.name }}" required>
          </div>
          <div class="form-row">
            <label for="edit-dept-slug-{{ department.pk }}">Slug</label>
            <input name="slug" id="edit-dept-slug-{{ department.pk }}" value="{{ department.slug }}" required>
          </div>
          <div class="form-row">
            <label for="edit-dept-description-{{ department.pk }}">Description</label>
            <textarea name="description" id="edit-dept-description-{{ department.pk }}" rows="3">{{ department.description }}</textarea>
          </div>
          <div class="form-row">
            <label for="edit-dept-color-{{ department.pk }}">Colour</label>
            <input type="color" name="color" id="edit-dept-color-{{ department.pk }}" value="{{ department.color }}">
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

### R4.2 Update `department_create` and `department_edit` in views

Both views currently return a full page render on invalid input. Since
the modal posts from the departments list page, both should redirect
back to `department_list` on success and on error.

Replace `department_create` with:

```
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
        messages.error(request, "Could not create department. Check the form.")
    return redirect("department_list")
```

Replace `department_edit` with:

```
@admin_required
def department_edit(request, pk):
    department = get_object_or_404(request.church.departments, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Department updated.")
        return redirect("department_list")
    if request.method == "POST":
        messages.error(request, "Could not update department. Check the form.")
    return redirect("department_list")
```

### R4.3 Add `department_delete` view and URL

In `church/views/admin_views.py`, add:

```
@admin_required
@require_POST
def department_delete(request, pk):
    department = get_object_or_404(request.church.departments, pk=pk)
    department.delete()
    messages.success(request, "Department deleted.")
    return redirect("department_list")
```

In `church/urls.py`, add after the existing `department_edit` path:

```
    path(
        "departments/<int:pk>/delete/",
        admin_views.department_delete,
        name="department_delete",
    ),
```

### R4.4 Verify

Run the two verification commands. Then visit `/departments/`:

1. **Click "New department"** — a modal opens.
2. **Submit** — redirects back to the list with the new department visible.
3. **Click "Edit"** on a row — modal opens with the current values.
4. **Click "Delete"** — browser confirm, then row disappears.

---

## Section R5 — Remove the Service dropdown from the announcement create modal

### R5.1 Edit `church/templates/church/announcements.html`

Find this block in the **create modal only** (around line 93–130):

```
        <div class="form-row">
          <label for="new-ann-service">Service (optional)</label>
          <select name="service" id="new-ann-service">
            <option value="">— All programmes —</option>
            {% for s in services %}
              <option value="{{ s.pk }}">{{ s.name }} — {{ s.date|date:"d M Y" }}</option>
            {% endfor %}
          </select>
        </div>
```

Delete it. The create modal should have only: announcement body, start
date, end date, and the show-on-public checkbox.

Do the same for the edit modals — remove the service dropdown block
from both the active-announcement edit modals and the upcoming-
announcement edit modals.

### R5.2 Remove `services` from the view context

In `church/views/admin_views.py`, in `announcement_list`, remove the
`services` query and the `"services": services,` line from the context.
The final render should be:

```
    return render(request, "church/announcements.html", {
        "active_announcements": active,
        "upcoming_announcements": upcoming,
        "older_announcements": older,
    })
```

### R5.3 Verify

Reload `/announcements/`, click "New announcement". The modal should
show only: announcement body, start date, end date, show-on-public
checkbox.

---

## Section R6 — Make the notification bell a floating button

The bell currently sits in the topbar and always occupies space. Change
it to a floating button that only appears when there are unread
notifications.

### R6.1 Update `church/templates/church/base.html`

Find the `.topbar` block:

```
      <header class="topbar">
        <div class="topbar-spacer"></div>
        <div class="topbar-actions">
          <div class="notif-bell" data-notification-root>
            <button class="icon-btn" type="button" data-notification-toggle aria-label="Notifications" hidden>
              <span aria-hidden="true">◔</span>
              <span class="notif-badge" data-notification-badge hidden>0</span>
            </button>
            <div class="notif-dropdown" data-notification-dropdown hidden></div>
          </div>
        </div>
      </header>
```

Replace with:

```
      {# Topbar is empty for now — notifications are a floating button #}
```

And move the notif-bell markup to just before the closing `</body>` tag,
right before the `<script src="{% static 'js/notifications.js' %}">` line:

```
  <div class="notif-bell notif-bell--floating" data-notification-root>
    <button class="icon-btn notif-float-btn" type="button" data-notification-toggle aria-label="Notifications" hidden>
      <span aria-hidden="true">◔</span>
      <span class="notif-badge" data-notification-badge hidden>0</span>
    </button>
    <div class="notif-dropdown" data-notification-dropdown hidden></div>
  </div>
```

Also delete the entire `<header class="topbar">` block — the whole
topbar is now empty and shouldn't take up space.

### R6.2 Append CSS to `static/css/harpr.css`

Append at the bottom of `static/css/harpr.css`:

```
/* ============================================================
   Notification bell — floating button
   ============================================================ */

.topbar {
  display: none;
}

.notif-bell--floating {
  position: fixed;
  right: var(--space-5);
  bottom: var(--space-5);
  z-index: 900;
}

.notif-float-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--accent);
  border: none;
  color: var(--accent-fg);
  box-shadow: 0 4px 14px rgba(40, 25, 10, 0.25);
  font-size: 1.1rem;
  cursor: pointer;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background .15s, transform .15s;
}

.notif-float-btn:hover {
  background: var(--accent-hover);
  transform: scale(1.05);
}

.notif-bell--floating .notif-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 9px;
  background: var(--danger);
  color: #fff;
  font-family: var(--font-sans);
  font-size: 0.68rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.notif-bell--floating .notif-dropdown {
  position: absolute;
  right: 0;
  bottom: calc(100% + 10px);
  top: auto;
  width: 320px;
  max-height: 420px;
  overflow-y: auto;
  padding: var(--space-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow-lg);
}

@media (max-width: 640px) {
  .notif-bell--floating {
    right: var
```