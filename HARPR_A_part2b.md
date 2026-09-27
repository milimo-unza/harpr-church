# Harpr — MD A, Part 2b: Announcements tail + Footer

**This is the continuation of part 2.** Part 2 was truncated at the
heading `<h2 class="section-label">Older</h2>` inside the
`announcements.html` template. This file picks up exactly there.

- Part 1 (applied): Sections A0.5 → A1.11
- Part 2 (applied up to A3.8): Sections A2.0 → A3.8
- **Part 2b (this file):** Sections A3.9 → A4.6
- Part 3 (after this): Sections A5 → A6.8

**Read this entire file before touching code. Do not read part 3 until told to. Do not re-apply parts 1 or 2.**

---

## Before you start

**Repo state:**

- Parts 1 and 2 are already applied.
- Part 2 stopped inside Section A3.8. The `announcements.html` file may
be incomplete on disk — the last heading written was `<h2 class="section-label">Older</h2>` with no table body following.
- `origin/main` is still at `165c305` — **do not push until Section A6.8 in part 3.**

**Verification after every section:**

```
python manage.py check
python manage.py test church
```

Both must pass. If either fails, stop and fix before continuing.

---

## Section A3.8 (completion) — Finish `church/templates/church/announcements.html`

**If Section A3.8 in part 2 was applied completely** (i.e. the file on
disk ends with `{% endblock %}` and contains the Older table), skip
this section and go to A3.9.

**Otherwise**, the file is incomplete. Replace the entire file with this
complete version:

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
{% endblock %}
```

Run the two verification commands.

---

## Section A3.9 — Update `announcement_list` view

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

    return render(request, "church/announcements.html", {
        "active_announcements": active,
        "upcoming_announcements": upcoming,
        "older_announcements": older,
    })
```

---

## Section A3.10 — Add pause and delete views

In `church/views/admin_views.py`, add after `announcement_edit`:

```
@admin_required
@require_POST
def announcement_pause(request, pk):
    announcement = get_object_or_404(request.church.announcements, pk=pk)
    announcement.is_paused = not announcement.is_paused
    announcement.save(update_fields=["is_paused"])
    state = "paused" if announcement.is_paused else "resumed"
    messages.success(request, f"Announcement {state}.")
    return redirect("announcement_list")

@admin_required
@require_POST
def announcement_delete(request, pk):
    announcement = get_object_or_404(request.church.announcements, pk=pk)
    announcement.delete()
    messages.success(request, "Announcement deleted.")
    return redirect("announcement_list")
```

---

## Section A3.11 — Add announcement URLs

In `church/urls.py`, add after the existing `announcement_edit` path:

```
    path(
        "announcements/<int:pk>/pause/",
        admin_views.announcement_pause,
        name="announcement_pause",
    ),
    path(
        "announcements/<int:pk>/delete/",
        admin_views.announcement_delete,
        name="announcement_delete",
    ),
```

Run the two verification commands.

---

## Section A3.12 — Replace `church/templates/church/public_schedule.html`

Overwrite the file completely:

```
{% extends "church/public_base.html" %}
{% block title %}{{ church.name }} · Programme{% endblock %}
{% block content %}
<p class="muted">{{ target_date|date:"l, d F Y" }}</p>

{% if service %}
  <div class="public-card">
    <div class="page-head">
      <h2>{{ service.name }}</h2>
      <a class="btn btn-primary" href="{% url 'public_bulletin_pdf' church.slug service.date.year service.date.month service.date.day %}">Download PDF</a>
    </div>
    <table class="public-table">
      <thead>
        <tr>
          <th>Time</th>
          <th>Item</th>
          <th>Department</th>
          <th>Assigned to</th>
        </tr>
      </thead>
      <tbody>
        {% for item in service.items.all %}
          <tr>
            <td class="mono">{{ item.planned_start|date:"H:i" }}</td>
            <td>{{ item.title }}</td>
            <td>{{ item.responsible_department.name|default:"—" }}</td>
            <td>
              {% for assignment in item.assignments.all %}
                {{ assignment.person_name }}{% if not forloop.last %}, {% endif %}
              {% empty %}—{% endfor %}
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
{% else %}
  <div class="public-card">
    <h2>No service scheduled today</h2>
    {% if next_service %}
      <p>Next programme: <a href="{% url 'public_schedule_date' church.slug next_service.date.year next_service.date.month next_service.date.day %}">{{ next_service.name }} on {{ next_service.date|date:"l, d F" }}</a></p>
    {% else %}
      <p>There is no upcoming programme yet.</p>
    {% endif %}
  </div>
{% endif %}

{% if announcements %}
  <section class="public-card">
    <h2>Announcements</h2>
    <ul class="public-links">
      {% for announcement in announcements %}
        <li>{{ announcement.body }}</li>
      {% endfor %}
    </ul>
  </section>
{% endif %}

<p class="public-links">
  <a href="{% url 'public_request' church.slug %}">Request to add something</a>
</p>

{% include "church/_public_footer.html" %}
{% endblock %}
```

---

## Section A3.13 — Update `_public_service_context`

In `church/views/public_views.py`, replace the announcements filter inside `_public_service_context` with:

```
    today = timezone.localdate()
    announcements = church.announcements.filter(
        is_paused=False,
        show_on_public=True,
        start_date__lte=today,
        end_date__gte=today,
    ).order_by("start_date")
```

The `today` variable may already exist inside that function — if so, do not duplicate the assignment. Reuse it.

Run the two verification commands.

---

## Section A4 — Footer fields and the public footer

### A4.1 Add footer fields to the Church model

In `church/models.py`, inside the `Church` class, add these four fields right after the `logo` field:

```
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_whatsapp = models.CharField(max_length=30, blank=True)
    footer_verse = models.CharField(max_length=300, blank=True)
```

### A4.2 Create the migration

Run:

```
python manage.py makemigrations church --name church_footer_fields
```

All four fields are blank, so Django will not prompt for defaults. Accept the migration and apply it:

```
python manage.py migrate
```

### A4.3 Replace `ChurchSettingsForm`

In `church/forms.py`, replace the `ChurchSettingsForm` class with:

```
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
        choices=AFRICAN_TIMEZONES, initial="Africa/Lusaka")

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
```

### A4.4 Create `church/templates/church/_public_footer.html`

```
{% if church.contact_phone or church.contact_email or church.contact_whatsapp or church.footer_verse %}
<section class="public-card public-footer">
  {% if church.footer_verse %}
    <p class="footer-verse"><em>{{ church.footer_verse }}</em></p>
  {% endif %}
  <div class="footer-contacts">
    {% if church.contact_phone %}
      <span><strong>Phone:</strong> {{ church.contact_phone }}</span>
    {% endif %}
    {% if church.contact_email %}
      <span><strong>Email:</strong> <a href="mailto:{{ church.contact_email }}">{{ church.contact_email }}</a></span>
    {% endif %}
    {% if church.contact_whatsapp %}
      <span>
        <strong>WhatsApp:</strong>
        <a href="https://wa.me/{{ church.contact_whatsapp }}" target="_blank" rel="noopener">Chat with us</a>
      </span>
    {% endif %}
  </div>
</section>
{% endif %}
```

### A4.5 Append footer CSS

Append at the bottom of `static/css/harpr.css`:

```
.public-footer {
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px solid var(--hairline);
  text-align: center;
}
.public-footer .footer-verse {
  font-family: var(--font-serif);
  font-size: 1rem;
  color: var(--muted-fg);
  margin: 0 0 var(--space-4);
}
.public-footer .footer-contacts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  justify-content: center;
  font-size: 0.86rem;
  color: var(--muted-fg);
}
.public-footer .footer-contacts a { color: var(--accent); }
```

### A4.6 Replace `church/templates/church/settings.html`

```
{% extends "church/base.html" %}
{% block title %}Settings · Harpr{% endblock %}
{% block content %}
<div class="narrow-page">
  <p class="eyebrow">Church profile</p>
  <h1>Settings</h1>
  <div class="card form-card">
    <form method="post" enctype="multipart/form-data">
      {% csrf_token %}
      {{ form.as_p }}
      <button class="btn btn-primary" type="submit">Save settings</button>
    </form>
  </div>
  <div class="card qr-display">
    <h2>Public schedule QR</h2>
    <img src="{% url 'church_qr' church.slug %}" alt="QR code for public schedule">
    <p class="muted">Timezone defaults to Africa/Lusaka.</p>
  </div>
</div>
{% endblock %}
```

Run the two verification commands. Then:

1. Sign in as coordinator.
2. Visit `/settings/` and fill in `contact_phone`, `contact_email`, `contact_whatsapp`, `footer_verse`. Save.
3. Visit `/c/grace-covenant/` — the footer should render with the WhatsApp link.
4. Visit any service detail page and click "Download PDF" — the PDF should have the announcements on page 2.

**STOP. Do not read part 3 of this spec until instructed.**

---

## End of part 2b

Report completion status with:

- Output of `python manage.py check`
- Output of `python manage.py test church`
- Output of `python manage.py makemigrations --check --dry-run` (should say "No changes detected" after A4.2)
- A one-line summary of the four manual checks above

Wait for instruction before proceeding to part 3.