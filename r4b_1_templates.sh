#!/bin/bash

# Round 4b, script 1 of 3.

# Rewrites the two broken templates (members.html and announcements.html)

# that are crashing the /members/ and /announcements/ pages.

# Also applies the auth-page scale-down CSS for the signup and login pages.

# Run from ~/harpr after activating the venv.

set -e
cd ~/harpr

echo "=== Backing up any existing versions ==="
mkdir -p .r4b_backup
cp church/templates/church/members.html .r4b_backup/members.html.bak 2>/dev/null || true
cp church/templates/church/announcements.html .r4b_backup/announcements.html.bak 2>/dev/null || true
cp static/css/harpr.css .r4b_backup/harpr.css.bak 2>/dev/null || true
echo "Backups saved to .r4b_backup/"

echo ""
echo "=== Rewriting members.html ==="
rm -f church/templates/church/members.html
cat > church/templates/church/members.html << 'ENDOFTEMPLATE'
{% extends "church/base.html" %}
{% block title %}Members · Harpr{% endblock %}
{% block content %}
<div class="page-head">
  <div>
    <p class="eyebrow">Access</p>
    <h1>Members</h1>
  </div>
  <button type="button" class="btn btn-primary" data-modal-open="invite-modal">Add member</button>
</div><div class="card table-wrap">
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
          <td>{{ m.user.email|default:"&mdash;" }}</td>
          <td>{{ m.get_role_display }}</td>
          <td>{{ m.department.name|default:"&mdash;" }}</td>
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
</div><div class="modal-backdrop" id="invite-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true">
    <div class="modal-head">
      <h2>Invite member</h2>
      <button type="button" class="icon-btn modal-close" aria-label="Close">&#x2715;</button>
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
            <option value="">&mdash; None &mdash;</option>
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
        <button type="button" class="icon-btn modal-close" aria-label="Close">&#x2715;</button>
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
              <option value="">&mdash; None &mdash;</option>
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
  </div>  <div class="modal-backdrop" id="deactivate-member-{{ m.pk }}" hidden>
    <div class="modal modal--narrow" role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>Deactivate member?</h2>
        <button type="button" class="icon-btn modal-close" aria-label="Close">&#x2715;</button>
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
  </div>  <div class="modal-backdrop" id="reactivate-member-{{ m.pk }}" hidden>
    <div class="modal modal--narrow" role="dialog" aria-modal="true">
      <div class="modal-head">
        <h2>Reactivate member?</h2>
        <button type="button" class="icon-btn modal-close" aria-label="Close">&#x2715;</button>
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
{% endfor %}<script>
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
ENDOFTEMPLATE

echo ""
echo "=== Rewriting announcements.html ==="
rm -f church/templates/church/announcements.html
cat > church/templates/church/announcements.html << 'ENDOFTEMPLATE'
{% extends "church/base.html" %}
{% block title %}Announcements · Harpr{% endblock %}
{% block content %}
<div class="page-head">
  <div>
    <p class="eyebrow">Public information</p>
    <h1>Announcements</h1>
  </div>
  <button type="button" class="btn btn-primary" data-modal-open="announcement-create-modal">New announcement</button>
</div><h2 class="section-label">Active</h2>
<div class="card table-wrap">
  <table class="data-table">
    <thead>
      <tr><th>Announcement</th><th>Runs</th><th>Public</th><th></th></tr>
    </thead>
    <tbody>
      {% for announcement in active_announcements %}
        <tr>
          <td>{{ announcement.body|truncatechars:80 }}</td>
          <td class="mono">{{ announcement.start_date|date:"d M" }} &rarr; {{ announcement.end_date|date:"d M Y" }}</td>
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
</div><h2 class="section-label">Upcoming</h2>
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
</div><h2 class="section-label">Older</h2>
<div class="card table-wrap">
  <table class="data-table">
    <thead>
      <tr><th>Announcement</th><th>Ran</th></tr>
    </thead>
    <tbody>
      {% for announcement in older_announcements %}
        <tr>
          <td>{{ announcement.body|truncatechars:80 }}</td>
          <td class="mono">{{ announcement.start_date|date:"d M" }} &rarr; {{ announcement.end_date|date:"d M Y" }}</td>
        </tr>
      {% empty %}
        <tr><td colspan="2" class="empty-state">No past announcements.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div><div class="modal-backdrop" id="announcement-create-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true">
    <div class="modal-head">
      <h2>New announcement</h2>
      <button type="button" class="icon-btn modal-close" aria-label="Close">&#x2715;</button>
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
        <button type="button" class="icon-btn modal-close" aria-label="Close">&#x2715;</button>
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
        <button type="button" class="icon-btn modal-close" aria-label="Close">&#x2715;</button>
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
{% endfor %}<script>
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
ENDOFTEMPLATE

echo ""
echo "=== Appending auth-page scale-down CSS ==="
cat >> static/css/harpr.css << 'ENDOFCSS'

/* ============================================================
Auth pages — global scale-down
============================================================ */

.auth-page {
font-size: 0.88rem;
}
.auth-topbar-mark {
width: 32px;
height: 32px;
font-size: 1.1rem;
border-radius: 8px;
}
.auth-topbar-brand strong {
font-size: 1.1rem;
}
.auth-topbar-brand small {
font-size: 0.6rem;
}
.auth-form-card,
.auth-form-card--wide {
max-width: 400px;
padding: var(--space-5);
}
.auth-form-card--wide {
max-width: 480px;
}
.auth-form-header {
margin-bottom: var(--space-4);
}
.auth-form-header h1 {
font-size: 1.35rem;
}
.auth-form-header .subtitle {
font-size: 0.82rem;
}
.auth-field {
margin-bottom: var(--space-3);
gap: 4px;
}
.auth-field label {
font-size: 0.78rem;
}
.auth-field input,
.auth-field select {
padding: 8px 11px;
font-size: 0.86rem;
}
.auth-field--password .pwd-toggle {
right: 4px;
bottom: 4px;
width: 30px;
height: 30px;
font-size: 0.85rem;
}
.auth-forgot {
font-size: 0.78rem;
margin-bottom: var(--space-3);
}
.auth-btn-primary {
padding: 9px 14px;
font-size: 0.86rem;
}
.auth-btn-outline {
padding: 8px 14px;
font-size: 0.86rem;
}
.auth-divider {
margin: var(--space-4) 0;
font-size: 0.76rem;
}
.auth-legal {
margin-top: var(--space-4);
font-size: 0.72rem;
}
.form-section {
margin-bottom: var(--space-4);
}
.form-section legend {
font-size: 0.66rem;
margin-bottom: var(--space-2);
}
.auth-error-banner {
padding: 8px 12px;
font-size: 0.8rem;
margin-bottom: var(--space-3);
}
ENDOFCSS

echo ""
echo "=== Verification ==="
echo "--- members.html ---"
wc -l church/templates/church/members.html
echo -n "extends: "; grep -c "{% extends" church/templates/church/members.html
echo -n "block title: "; grep -c "{% block title" church/templates/church/members.html
echo -n "block content: "; grep -c "{% block content" church/templates/church/members.html
echo -n "endblock: "; grep -c "{% endblock" church/templates/church/members.html
echo -n "bad operator (m.role==): "; grep -c "m.role==" church/templates/church/members.html || echo 0
echo ""
echo "--- announcements.html ---"
wc -l church/templates/church/announcements.html
echo -n "extends: "; grep -c "{% extends" church/templates/church/announcements.html
echo -n "block title: "; grep -c "{% block title" church/templates/church/announcements.html
echo -n "block content: "; grep -c "{% block content" church/templates/church/announcements.html
echo ""
echo "--- harpr.css size ---"
wc -l static/css/harpr.css
echo ""
echo "=== Django verification ==="
. .venv/bin/activate
python manage.py check
python manage.py test church

echo ""
echo "=== Done. ==="