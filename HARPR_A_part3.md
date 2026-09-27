# Harpr — MD A, Part 3 of 3: Modals, Sidebar, Mobile, Push

**This is part 3 of a three-part spec. This is the final part.**

- Part 1 (already applied): Sections A0.5 → A1.11
- Part 2 (already applied): Sections A2 → A4
- **Part 3 (this file):** Sections A5 → A6.8

**Read this entire file before touching code.**

---

## Before you start

**Repo state:**

- Parts 1 and 2 must already be applied and green. If they aren't, stop and complete them first.
- `origin/main` is still at `165c305` — this part performs the first push.
- Two spec files exist in the repo root and must NOT be committed until A6.8:

- `HARPR_MD_A_v2.md`
- `HARPR_MD_A_TRUNCATED_DO_NOT_USE.md`

**Verification after every section:**

```
python manage.py check
python manage.py test church
```

Both must pass. If either fails, stop and fix before continuing.

**Files not to touch:**

- `church/services/recalculation.py`
- `church/services/qr.py`
- `church/migrations/0001_*` through `0005_*`
- `manage.py`, `harpr_church/wsgi.py`, `harpr_church/asgi.py`

**Editing rules:**

- "Replace" = overwrite the file completely
- "Append" = add at the very bottom of the file
- "Add" = insert at the specified location without removing anything

---

## Section A5 — Notification bell

The notification bell in `church/templates/church/base.html` currently renders on every page but never hides when there are zero unread notifications. This section fixes that.

### A5.1 Update the notification block in `base.html`

In `church/templates/church/base.html`, find:

```
          <div class="notif-bell" data-notification-root>
            <button class="icon-btn" type="button" data-notification-toggle aria-label="Notifications">
              <span aria-hidden="true">◔</span>
              <span class="notif-badge" data-notification-badge hidden>0</span>
            </button>
            <div class="notif-dropdown" data-notification-dropdown hidden></div>
          </div>
```

Replace it with:

```
          <div class="notif-bell" data-notification-root>
            <button class="icon-btn" type="button" data-notification-toggle aria-label="Notifications" hidden>
              <span aria-hidden="true">◔</span>
              <span class="notif-badge" data-notification-badge hidden>0</span>
            </button>
            <div class="notif-dropdown" data-notification-dropdown hidden></div>
          </div>
```

The added `hidden` attribute means the bell does not flash on first paint. `notifications.js` reveals it only when there is at least one unread notification.

### A5.2 Replace `static/js/notifications.js`

```
(function () {
  var root = document.querySelector("[data-notification-root]");
  if (!root) return;
  var badge = root.querySelector("[data-notification-badge]");
  var dropdown = root.querySelector("[data-notification-dropdown]");
  var toggle = root.querySelector("[data-notification-toggle]");

  function hideBell() {
    if (toggle) toggle.hidden = true;
  }

  function showBell() {
    if (toggle) toggle.hidden = false;
  }

  function loadNotifications() {
    fetch("/api/notifications/", {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (response) {
        return response.ok ? response.json() : null;
      })
      .then(function (data) {
        if (!data) return;

        if (data.unread_count === 0) {
          hideBell();
          badge.hidden = true;
          return;
        }

        showBell();
        badge.textContent = data.unread_count;
        badge.hidden = false;
        dropdown.innerHTML = data.notifications.length
          ? data.notifications
              .map(function (item) {
                return (
                  '<a class="notif-item" href="' + item.url + '">' +
                  "<strong>" + item.title + "</strong>" +
                  "<small>" + item.body + "</small>" +
                  "</a>"
                );
              })
              .join("")
          : '<div class="notif-item">No new notifications.</div>';
      })
      .catch(function () {});
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      dropdown.hidden = !dropdown.hidden;
      if (!dropdown.hidden) loadNotifications();
    });
  }

  hideBell();
  loadNotifications();
  window.setInterval(loadNotifications, 60000);
})();
```

### A5.3 Verify

Run the two verification commands.

1. Visit `/dashboard/` with the coordinator account. The bell should not be visible (no unread notifications after a fresh seed).
2. Trigger a notification: go to `/members/`, deactivate a member. That member now has a notification.
3. Log in as that deactivated member (impossible — they're deactivated). Instead: log back in as coordinator, visit `/members/`, edit any member's role. That member gets a notification but the coordinator doesn't.
4. To test the bell appearing for yourself, run in a Django shell:

```
python manage.py shell
```

Then:

```
from django.contrib.auth import get_user_model
from church.services.notifications import notify_user
from church.models import Church
User = get_user_model()
u = User.objects.get(username="coordinator")
c = Church.objects.get(slug="grace-covenant")
notify_user(u, "Test notification", "This is a test.", church=c)
```

Reload `/dashboard/` — the bell should now appear with a badge.

---

## Section A6 — Modals, sidebar, mobile, final push

### A6.1 Append modal and section-label CSS

Append at the very bottom of `static/css/harpr.css`:

```
.modal-backdrop[hidden] { display: none !important; }

.section-label {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted-fg);
  margin: var(--space-5) 0 var(--space-3);
}
.section-label:first-of-type { margin-top: 0; }

@media (max-width: 640px) {
  .modal {
    max-width: none;
    margin: 0;
    border-radius: var(--radius) var(--radius) 0 0;
    align-self: flex-end;
  }
  .modal-backdrop {
    align-items: flex-end;
    padding: 0;
  }
  .modal-body { padding: var(--space-4); }
  .modal-head { padding: var(--space-4); }
  .modal .form-actions {
    flex-direction: column-reverse;
  }
  .modal .form-actions .btn { width: 100%; }

  .table-wrap {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .data-table, .public-table { font-size: 0.8rem; }
  .data-table th, .data-table td,
  .public-table th, .public-table td { padding: 6px 8px; }

  .form-row.two-up { grid-template-columns: 1fr; }
}
```

### A6.2 Remove "New event" from the sidebar

In `church/templates/church/base.html`, delete this line from the coordinator navigation:

```
          <a class="navlink {% if request.resolver_match.url_name == 'event_create' or request.resolver_match.url_name == 'event_edit' %}active{% endif %}" href="{% url 'event_create' %}">New event</a>
```

New events will be created from the dashboard modal (see A6.3).

### A6.3 Replace `church/templates/church/dashboard.html`

Overwrite the file completely. This adds an event-create modal, keeps the "New service" as a link (service creation is more complex and stays a full page), and wires up the modal script.

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
    <a class="btn btn-ghost" href="{% url 'service_create' %}">New service</a>
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

{# ---------- Event create modal ---------- #}
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

**Note on the department dropdown:** the template uses `church.departments.all` which requires `church` to be in the context. `admin_dashboard` already passes it. If you find the dropdown is empty, add `departments` to the context in `admin_dashboard`:

```
            "departments": request.church.departments.all(),
```

And change the template to `{% for d in departments %}`.

### A6.4 Logout redirect to home

In `harpr_church/settings.py`, find:

```
LOGOUT_REDIRECT_URL = "login"
```

Replace with:

```
LOGOUT_REDIRECT_URL = "home"
```

### A6.5 Sunday-first week

In `church/views/admin_views.py`, inside `admin_dashboard`, find:

```
    week_start = today - timedelta(days=today.weekday())
```

Replace with:

```
    # Sunday-first week: Sunday.weekday() == 6, so shift forward by 1
    days_since_sunday = (today.weekday() + 1) % 7
    week_start = today - timedelta(days=days_since_sunday)
```

### A6.6 Verify 24-hour time everywhere

Search the codebase for templates that display time with AM/PM:

```
grep -rn "time:.*A" church/templates/ templates/
grep -rn "time:.*a\"" church/templates/ templates/
```

Any match containing `A` or `a` at the end of a `time:` format string is displaying AM/PM. The correct format is `time:"H:i"` — 24-hour, zero-padded. Replace each match.

The existing templates already use `time:"H:i"` in most places. This is a verification pass — if you find no matches, note that in your report and continue.

### A6.7 Mobile responsiveness sweep

Open each template in a browser at 375px width (or use Firefox/Chrome device toolbar) and verify the layout works. Fix any that break by adding a media query at the very bottom of `harpr.css`. The two breakpoints are already defined in A6.1:

- `@media (max-width: 1024px)` — tablet
- `@media (max-width: 640px)` — phone

Templates to check:

1. `church/templates/church/dashboard.html`
2. `church/templates/church/members.html`
3. `church/templates/church/announcements.html`
4. `church/templates/church/service_detail.html`
5. `church/templates/church/service_list.html`
6. `church/templates/church/public_schedule.html`
7. `church/templates/auth/login.html`
8. `templates/signup/church_signup.html`

The `.table-wrap` overflow rule from A6.1 handles the tables. The `.form-row.two-up` stacking rule handles the forms. If any template still breaks, add a specific media query for that template's selectors.

### A6.8 Final commit and push

**Before committing**, run all three of these:

```
python manage.py check
python manage.py test church
python manage.py makemigrations --check --dry-run
```

The last one should print "No changes detected." If it reports any pending migrations, run `makemigrations`, apply them with `migrate`, and commit those too.

Then commit and push:

```
git add -A
git commit -m "MD A v2: login redesign, members table, announcement lifecycle, footer, mobile fixes"
git push origin main
```

Report the **full output of `git push origin main`**.

Then remove the spec files and push again:

```
git rm HARPR_MD_A_v2.md
git rm HARPR_MD_A_TRUNCATED_DO_NOT_USE.md
git commit -m "Remove applied spec files"
git push origin main
```

Report the full output of that second push.

If at any point a command fails, stop and report the exact error.

---

## End of part 3

After both pushes complete, MD A is done. Report:

- Output of `python manage.py check`
- Output of `python manage.py test church`
- Output of `python manage.py makemigrations --check --dry-run`
- Output of both `git push` commands
- A short summary: which files were created, modified, deleted across the whole of MD A

Do not begin any other work until the user reviews this.