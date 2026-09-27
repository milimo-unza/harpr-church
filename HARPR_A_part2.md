# Harpr — MD A, Part 2 of 3: Members, Announcements, Footer

**This is part 2 of a three-part spec.**

- Part 1 (already applied): Sections A0.5 → A1.11
- **Part 2 (this file):** Sections A2 → A4
- Part 3: Sections A5 → A6.8

**Read this entire file before touching code. Do not read part 3 until told to. Do not re-apply part 1.**

---

## Before you start

**Repo state:**

- Part 1 must already be applied and green. If it isn't, stop and complete it first.
- HEAD should be at or ahead of `b46567b`.
- `origin/main` is still at `165c305` — **do not push until Section A6.8 in part 3.**

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

## Section A2.0 — Trim `MemberInviteForm` to email + role + department

The current `MemberInviteForm` asks the administrator for the invitee's username and name at invite time. That is wrong for the invitation-only flow: the invitee sets their own username, name, phone, and password when they accept. The form should only ask for email, role, and department.

### A2.0.1 Replace `MemberInviteForm`

In `church/forms.py`, replace the entire `MemberInviteForm` class with:

```
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
```

### A2.0.2 Update `member_invite` view

In `church/views/admin_views.py`, find the `member_invite` function and replace it with:

```
@admin_required
def member_invite(request):
    import secrets
    from django.core.mail import send_mail
    from django.urls import reverse

    form = MemberInviteForm(request.POST or None, church=request.church)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        token = secrets.token_urlsafe(32)
        Invitation.objects.create(
            church=request.church,
            email=data["email"],
            role=data["role"],
            department=data.get("department"),
            token=token,
            invited_by=request.user,
        )
        accept_url = request.build_absolute_uri(
            reverse("accept_invitation", kwargs={"token": token})
        )
        send_mail(
            subject=f"You're invited to join {request.church.name} on Harpr",
            message=(
                f"{request.user.get_full_name() or request.user.username} "
                f"has invited you to join {request.church.name} on Harpr.\n\n"
                f"Click this link to set your password and accept:\n"
                f"{accept_url}\n\n"
                f"This link expires in 7 days and can only be used once."
            ),
            from_email="harpr@localhost",
            recipient_list=[data["email"]],
            fail_silently=False,
        )
        messages.success(request, f"Invitation sent to {data['email']}.")
        return redirect("member_list")
    return render(
        request,
        "church/member_form.html",
        {"form": form, "title": "Invite member"},
    )
```

Run the two verification commands.

---

## Section A2 — Members table, inline actions, modals, reactivation

### A2.1 Update the `member_list` view

In `church/views/admin_views.py`, replace `member_list` with:

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

### A2.2 Add the `member_reactivate` view

In `church/views/admin_views.py`, add after `member_deactivate`:

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
    membership.save(update_fields=["is_active"])

    notify_user(
        membership.user,
        "Your account has been reactivated",
        f"Your access to {request.church.name} has been restored.",
        church=request.church,
    )
    messages.success(request, f"{membership.user.username} reactivated.")
    return redirect("member_list")
```

### A2.3 Notify deactivated members

Replace `member_deactivate` with:

```
@admin_required
@require_POST
def member_deactivate(request, pk):
    membership = get_object_or_404(request.church.memberships, pk=pk)
    membership.is_active = False
    membership.save(update_fields=["is_active"])

    notify_user(
        membership.user,
        "Your account has been deactivated",
        f"Your access to {request.church.name} has been suspended by an administrator.",
        church=request.church,
    )
    messages.success(request, f"{membership.user.username} deactivated.")
    return redirect("member_list")
```

### A2.4 Add the reactivate URL

In `church/urls.py`, add right after the `member_deactivate` path:

```
    path(
        "members/<int:pk>/reactivate/",
        admin_views.member_reactivate,
        name="member_reactivate",
    ),
```

### A2.5 Lock down `MemberEditForm`

Replace `MemberEditForm` in `church/forms.py` with:

```
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
```

### A2.6 Update `member_edit`

Replace `member_edit` in `church/views/admin_views.py` with:

```
@admin_required
def member_edit(request, pk):
    membership = get_object_or_404(
        request.church.memberships.select_related("user"), pk=pk
    )
    form = MemberEditForm(
        request.POST or None,
        church=request.church,
        initial={
            "role": membership.role,
            "department": membership.department_id,
        },
    )
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        membership.role = data["role"]
        membership.department = data["department"]
        membership.save(update_fields=["role", "department"])

        notify_user(
            membership.user,
            "Your role has been updated",
            f"Your role in {request.church.name} is now {membership.get_role_display()}.",
            church=request.church,
        )
        messages.success(request, "Member updated.")
        return redirect("member_list")

    return render(
        request,
        "church/member_form.html",
        {"form": form, "membership": membership, "title": "Edit member"},
    )
```

### A2.7 Append modal CSS to `static/css/harpr.css`

Append at the very bottom of the file:

```
/* ====================== MODALS ====================== */

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(20, 15, 8, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  z-index: 1000;
}
.modal-backdrop[hidden] { display: none; }

.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(40, 25, 10, 0.18);
}
.modal--narrow { max-width: 420px; }

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--hairline);
}
.modal-head h2 {
  font-family: var(--font-serif);
  font-size: 1.15rem;
  font-weight: 500;
  margin: 0;
}
.modal-head .icon-btn {
  width: 28px;
  height: 28px;
  font-size: 0.9rem;
}

.modal-body {
  padding: var(--space-5);
  overflow-y: auto;
}
.modal-body p { margin-top: 0; }

.modal .form-row { margin-bottom: var(--space-4); }
.modal .form-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
  margin-top: var(--space-5);
  padding-top: var(--space-4);
  border-top: 1px solid var(--hairline);
}

.row-actions-inline {
  display: flex;
  gap: var(--space-2);
  align-items: center;
  white-space: nowrap;
}
```

Run the two verification commands.

### A2.8 Replace `church/templates/church/members.html`

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
        <th scope="col">Username</th>
        <th scope="col">Name</th>
        <th scope="col">Email</th>
        <th scope="col">Role</th>
        <th scope="col">Department</th>
        <th scope="col">Status</th>
        <th scope="col"></th>
      </tr>
    </thead>
    <tbody>
      {% for m in memberships %}
        <tr>
          <td>{{ m.user.username }}</td>
          <td>{{ m.user.get_full_name|default:"—" }}</td>
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
        <tr><td colspan="7" class="empty-state">No members yet.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>

{# ---------- Invite modal ---------- #}
<div class="modal-backdrop" id="invite-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="invite-title">
    <div class="modal-head">
      <h2 id="invite-title">Invite member</h2>
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
        <p>Deactivating <strong>{{ m.user.username }}</strong> will prevent them from signing in. They will receive an email notification. Their historical entries remain in the system.</p>
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

Run the two verification commands. Visit `/members/` and confirm:

- Edit and Deactivate appear on one line per row
- Edit opens a modal with only Role and Department
- Deactivate opens a confirm modal
- Deactivated members show a Reactivate button
- Reactivate opens a modal asking for your password

---

## Section A3 — Announcements lifecycle

This rewrites the `Announcement` model: drops `title`, adds `start_date`, `end_date`, and `is_paused`. Also updates the PDF to put announcements on page 2 and rewrites the seed data.

### A3.1 Replace the `Announcement` model

In `church/models.py`, replace the entire `Announcement` class:

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
        return f"{self.church.name} — {self.body[:40]}"

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

### A3.2 Create the migration with a data-migration step

Run:

```
python manage.py makemigrations church --name announcement_lifecycle
```

Django will prompt for a default for `start_date` and `end_date` because existing rows have neither. Choose **"Provide a one-off default now"** for both and enter:

- `start_date` → `django.utils.timezone.now`
- `end_date` → `django.utils.timezone.now`

Django will ask about removing `title`, `is_active`, and `expires_at`. Accept each removal.

After the migration file is generated, open it and add a data-migration step so no information is lost. At the top of the file, add:

```
from datetime import timedelta
from django.utils import timezone
```

Above the `Migration` class, add:

```
def fold_title_into_body(apps, schema_editor):
    """Fold existing title into body so nothing is lost."""
    Announcement = apps.get_model("church", "Announcement")
    today = timezone.localdate()
    for announcement in Announcement.objects.all():
        title = getattr(announcement, "title", "") or ""
        if title and announcement.body:
            announcement.body = f"{title}. {announcement.body}"
        elif title:
            announcement.body = title
        if not announcement.start_date:
            announcement.start_date = today
        if not announcement.end_date:
            announcement.end_date = today + timedelta(days=30)
        announcement.save()
```

Inside the `operations` list, add this as the **first** operation:

```
        migrations.RunPython(
            fold_title_into_body, migrations.RunPython.noop
        ),
```

Apply the migration:

```
python manage.py migrate
```

Run the two verification commands.

### A3.3 Rewrite `seed_demo.py` — announcements

Open `church/management/commands/seed_demo.py`. Find the two `Announcement.objects.update_or_create` blocks at the end of `handle` and delete them. Replace with:

```
        today = timezone.localdate()

        # ---------- Announcements: full lifecycle coverage ----------
        Announcement.objects.filter(church=church).delete()

        Announcement.objects.create(
            church=church,
            body="Mid-week prayer meeting moves to Wednesday at 18:00 in the main sanctuary. All are welcome.",
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
            is_paused=False,
            show_on_public=True,
        )
        Announcement.objects.create(
            church=church,
            body="The choir is recruiting new members. Speak to the music department after service.",
            start_date=today - timedelta(days=45),
            end_date=today - timedelta(days=15),
            is_paused=False,
            show_on_public=True,
        )
        Announcement.objects.create(
            church=church,
            body="Monthly outreach to Matero is this Saturday at 09:00. Meet at the church car park.",
            start_date=today - timedelta(days=7),
            end_date=today + timedelta(days=7),
            is_paused=False,
            show_on_public=True,
        )
        Announcement.objects.create(
            church=church,
            body="Harvest thanksgiving service is on the last Sunday of October. Bring your family.",
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=20),
            is_paused=False,
            show_on_public=True,
        )
        Announcement.objects.create(
            church=church,
            body="Youth camp registration closes at the end of the month. Forms are at the welcome desk.",
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=40),
            is_paused=False,
            show_on_public=True,
        )
        Announcement.objects.create(
            church=church,
            body="New believers' class begins next month. Sign up with the pastors' department.",
            start_date=today + timedelta(days=14),
            end_date=today + timedelta(days=60),
            is_paused=False,
            show_on_public=True,
        )
```

### A3.4 Rewrite `seed_demo.py` — the services timeline

Find this block in `seed_demo.py`:

```
        sunday = timezone.localdate() - timedelta(days=(timezone.localdate().weekday() + 1) % 7)
        names = {
            "Sermon": ["Pastor Phiri", "Pastor Banda", "Pastor Mulenga"],
            "Worship Songs": ["Ruth Mwansa", "Mwaka Zulu", "Chanda Tembo"],
            "Offering": ["Moses Lungu", "Esther Chileshe", "Andrew Sakala"],
            "Scripture Reading": ["Grace Mumba", "Brian Kunda", "Naomi Sampa"],
        }
        valid_service_dates = [
            sunday + timedelta(days=week * 7) for week in range(-3, 5)
        ]
```

Replace it with:

```
        # ---------- Services: July through November 2026 ----------
        anchor = date(2026, 7, 5)
        end = date(2026, 11, 29)
        valid_service_dates = []
        cursor = anchor
        while cursor <= end:
            valid_service_dates.append(cursor)
            cursor += timedelta(days=7)

        names = {
            "Sermon": ["Pastor Phiri", "Pastor Banda", "Pastor Mulenga"],
            "Worship Songs": ["Ruth Mwansa", "Mwaka Zulu", "Chanda Tembo"],
            "Offering": ["Moses Lungu", "Esther Chileshe", "Andrew Sakala"],
            "Scripture Reading": ["Grace Mumba", "Brian Kunda", "Naomi Sampa"],
        }
```

Make sure `from datetime import date` is imported at the top of the file. It usually already is.

### A3.5 Rewrite `seed_demo.py` — the events timeline

Find the block that creates `ChurchEvent` rows. It currently creates five events on a single week. Replace it with:

```
        # ---------- Events: spread across the active period ----------
        ChurchEvent.objects.filter(church=church).delete()

        event_templates = [
            ("Choir Practice", "rehearsal", 2, time(18, 0), time(19, 30), "music"),
            ("Bible Study", "study", 4, time(18, 30), time(20, 0), "pastors"),
            ("Youth Meeting", "meeting", 5, time(14, 0), time(16, 0), "children"),
            ("Prayer Meeting", "meeting", 5, time(9, 0), time(11, 0), "prayer"),
            ("Media Team Rehearsal", "rehearsal", 1, time(17, 0), time(18, 0), "media"),
            ("Ushering Team Briefing", "meeting", 3, time(17, 30), time(18, 30), "ushering"),
            ("Community Outreach", "outreach", 6, time(9, 0), time(13, 0), "pastors"),
        ]

        event_weeks = [anchor + timedelta(weeks=i) for i in range(0, 22, 3)]
        for week_start in event_weeks:
            for title, event_type, day_offset, start_time, end_time, dept_slug in event_templates:
                ChurchEvent.objects.create(
                    church=church,
                    title=title,
                    event_type=event_type,
                    date=week_start + timedelta(days=day_offset),
                    start_time=start_time,
                    end_time=end_time,
                    location="Main church campus",
                    responsible_department=departments.get(dept_slug),
                )
```

This uses `anchor` from A3.4. Apply A3.4 first.

### A3.6 Replace `AnnouncementForm`

In `church/forms.py`, replace the `AnnouncementForm` class with:

```
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

    def __init__(self, *args, church=None, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        self.fields["service"].required = False
        self.fields["service"].queryset = (
            church.services.all() if church else Service.objects.none()
        )
        if instance is None:
            self.fields["start_date"].initial = timezone.localdate()
        _style_fields(self)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")

        if not self.instance.pk and start and start < timezone.localdate():
            raise forms.ValidationError(
                "New announcements cannot start in the past. "
                "Choose today or a future date."
            )

        if start and end and end < start:
            raise forms.ValidationError(
                "The end date must be on or after the start date."
            )
        return cleaned
```

### A3.7 Update `pdf.py` — announcements on page 2

In `church/services/pdf.py`, find the imports line:

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

Then find the announcements block at the bottom of `generate_bulletin_pdf` and replace it entirely with:

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

### A3.8 Replace `church/templates/church/announcements.html`

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
            <a class="btn btn-small" href="{% url 'announcement_edit' announcement.pk %}">Edit</a>
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
            <a class="btn btn-small" href="{% url 'announcement_edit' announcement.pk %}">Edit</a>
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
```