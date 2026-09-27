# Harpr — MD A, Part 1 of 3: CSS cleanup + auth redesign

**This is part 1 of a three-part spec.** It is calibrated against the
actual repo state at commit `b46567b`.

- **Part 1 (this file):** Sections A0.5 → A1.11
- Part 2: Sections A2 → A4
- Part 3: Sections A5 → A6.8

**Read this entire file before touching code. Do not read part 2 until
told to.**

---

## Before you start

**Repo state:**

- HEAD is `b46567b` (`A0: remove dead login templates and dead CSS files`)
- `origin/main` is at `165c305` — **do not push until Section A6.8 in part 3**
- Section A0 is already applied. Do not redo it.
- The working tree has one untracked file: `HARPR_MD_A_v2.md` (this
spec, in three parts). Do not commit it until A6.8.

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
- Never truncate. If you run out of space, stop and report.

---

## Section A0.5 — Strip dead planner CSS from `static/css/harpr.css`

`static/css/harpr.css` contains a large block of CSS left over from the
earlier "task planner" version of this project. None of it matches any
template in the church app. It is dead weight that fights the church
styles and makes the typography look wrong.

**Do NOT replace the file.** Open it and remove only the blocks listed
below. Every line not mentioned stays exactly as it is.

If you are unsure whether to remove something, leave it in and note it
in your final report.

### A0.5.1 Remove the Pomodoro block

Delete the block starting with:

```
/* ====================== pomodoro ====================== */
```

and every rule that begins with `.pomodoro`, `.pomodoro-`, or
`.pomodoro-settings-btn` anywhere in the file. There are several
scattered. Search for `.pomodoro` and remove each match.

### A0.5.2 Remove the category chip block

Delete the block starting with:

```
/* ====================== category chips ====================== */
```

and every rule containing `.cat-chip` or `.cat-tag` anywhere in the
file. These reference work/study/personal/health categories that do not
exist in the church app.

### A0.5.3 Remove the activity log block

Delete the block starting with:

```
/* ====================== activity log ====================== */
```

and every rule containing any of: `.activity-list`, `.activity-time`,
`.activity-action`, `.act-created`, `.act-updated`, `.act-completed`,
`.act-reopened`, `.act-deleted`, `.act-restored`, `.activity-task`,
`.activity-undo`.

### A0.5.4 Remove the timeline blocks

Delete every rule containing: `.timeline-scroll`, `.timeline-group`,
`.timeline-group-head`, `.timeline-group.is-today`.

### A0.5.5 Remove the FullCalendar blocks

Delete every rule whose selector begins with `#calendar`. This includes
all `#calendar .fc-*` rules, `#calendar .chip-holiday`,
`#calendar .chip-task`, `#calendar .harpr-chips`, `#calendar .harpr-more`,
`#calendar .fc-scrollgrid`, and any rule of the form
`.week-col .chip-task`. The church app has no FullCalendar integration.

### A0.5.6 Remove the mobile bottom-nav

Delete the block starting with:

```
/* ====================== mobile bottom-nav ====================== */
```

and every rule containing `.mobile-nav`, `.mobile-nav-item`, or
`.mobile-nav-glyph`.

### A0.5.7 Remove the "Visual downscale" and sibling blocks

Delete every block whose opening comment matches any of:

- `/* ============ Visual downscale`
- `/* ============ Muted category colours`
- `/* ============ Task row: clean 3-column grid`
- `/* ============ Category tag`
- `/* ============ Lowercase category tags`
- `/* ============ Timeline on mobile`
- `/* ============ Mobile: Calendar toolbar`
- `/* ============ Mobile: Activity list`
- `/* ============ Utility: visibility toggles`
- `/* ============ Insights card on Today`
- `/* ============ Quick add bar on Today`
- `/* ============ Auth card: brand + tagline`

Delete each such block and everything in it.

### A0.5.8 Remove the font-size overrides

Delete every rule anywhere in the file of the form:

```
html { font-size: ... }
html { font-size: ... !important; }
```

There will be several. The base `html { font-size: 15px; }` near the top
of the file is the ONLY one that should remain.

### A0.5.9 Remove old-planner selectors

Delete every rule containing any of these selectors:

```
.auth-shell
.auth-brand
.auth-card--wide
.reminders-pip
.reminders-pip--hint
.settings-grid
.settings-card
.setting-row
.setting-copy
.setting-help
.setting-control
.settings-save
.quick-add
.chart-tabs
.chart-tab
.insights-kpis
.insight-kpi
.insight-num
.insight-unit
.insight-label
.insights-chart-wrap
.insights-canvas
.week-toolbar
.view-tab
.cal-toolbar
.cal-card
.cal-view
.list-day-group
.list-day-head
.list-row
.list-time
.list-title
.week-empty
.week-holiday
.week-col-label
.week-col-day
.week-col.is-today
.desktop-only
.mobile-only
.dot-priority
.dot-overdue
.dot-high
.dot-medium
.dot-low
.overdue-card
.overdue-row
.overdue-action
.task-scroll
.task-scroll--hidden
.task-form
.task-form-toggle
.task-row
.task-title
.task-meta
.task-main
.task-list
.dashboard-list
```

**Warning:** `.week-col.is-today` is in this list, but the church app
DOES have a `.week-col.today` rule. Only remove `.week-col.is-today`
(with the `is-` prefix). Leave `.week-col.today` alone.

### A0.5.10 Verify

After the deletions, the file should contain roughly this in order:

1. `:root` and `[data-theme="dark"]` variable declarations
2. Global resets: `*`, `html`, `body`, `h1`–`h4`, `a`, `.nowrap`,
`.mono`, `.muted`
3. `.layout`, `.sidebar`, `.sidenav`, `.navlink`, `.sidebar-footer`,
`.user-chip`, `.footer-actions`, `.icon-btn`
4. `.main`, `.topbar`, `.page-head`, `.eyebrow`
5. `.card`, `.card-head`
6. `.btn`, `.btn-primary`, `.btn-ghost`, `.btn-danger`, `.btn-small`,
`.btn-block`
7. `.form-row`, `.form-row.two-up`, `.form-row label`,
`.form-row input`, `.form-row select`, `.form-row textarea`
8. `.form-actions`, `.form-error`, `.errorlist`
9. `.data-table`, `.public-table`
10. `.empty-state`, `.assignee-list`
11. `.stat-grid`, `.stat-card`, `.stat-value`, `.stat-label`
12. `.week-nav`, `.week-grid`, `.week-col`, `.week-col-head`,
`.week-col-body`, `.event-chip`, `.empty-day`
13. `.attention-card`, `.attention-list`
14. `.status-badge` and variants
15. `.freeze-banner`
16. `.filter-tabs`
17. `.notif-bell`, `.notif-badge`, `.notif-dropdown`, `.notif-item`
18. `.toast-stack`, `.toast`, `.toast--success`, `.toast--error`,
`.toast--info`
19. `.row-actions`, `.inline-details`, `.inline-form-stack`,
`.inline-form`
20. `.auth-body`, `.auth-card`, `.auth-foot` (these are old auth styles
— they will be superseded in A1, but leave them for now)
21. `.public-body`, `.public-shell`, `.public-head`, `.public-card`,
`.public-card-head`, `.public-announcement`, `.public-links`,
`.saved-list`
22. Two media queries at the bottom for `max-width: 1024px` and
`max-width: 768px`

The file will be roughly 60% shorter than before. That is expected.

Run:

```
python manage.py check
python manage.py test church
```

Start the dev server and visit `/accounts/login/` and `/dashboard/`.
Both should render correctly but look unfinished. If anything is
visibly broken, restore the rule you removed and note it.

---

## Section A1 — Login, signup, invitation, password reset redesign

The new design is a centered card with the brand mark top-left of the
page, a "Welcome back!" heading centered in the card, a red error
banner above the form when credentials are wrong, password fields with
a show/hide eye, a full-width primary button, a divider with "New to
Harpr?", an outlined secondary button, and a legal footer. A
back-to-home link and a theme toggle sit in the top-right.

### A1.1 Append auth CSS to `static/css/harpr.css`

Append at the very bottom of the file:

```
/* ====================== AUTH PAGES ====================== */

.auth-page {
  min-height: 100vh;
  background: var(--bg);
  display: flex;
  flex-direction: column;
  padding: var(--space-5);
}

.auth-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
  flex-wrap: wrap;
  gap: var(--space-3);
}
.auth-topbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.auth-topbar-mark {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--accent);
  color: var(--accent-fg);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-serif);
  font-size: 1.35rem;
  font-weight: 600;
}
.auth-topbar-brand {
  display: flex;
  flex-direction: column;
}
.auth-topbar-brand strong {
  font-family: var(--font-serif);
  font-size: 1.35rem;
  font-weight: 500;
  line-height: 1;
}
.auth-topbar-brand small {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted-fg);
  margin-top: 4px;
}
.auth-topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.auth-topbar-actions a {
  font-size: 0.86rem;
  color: var(--muted-fg);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
}
.auth-topbar-actions a:hover {
  color: var(--fg);
  background: var(--surface-2);
}

.auth-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-5) 0;
}

.auth-form-card {
  width: 100%;
  max-width: 420px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-6);
}
.auth-form-card--wide { max-width: 560px; }

.auth-form-header {
  text-align: center;
  margin-bottom: var(--space-5);
}
.auth-form-header h1 {
  font-family: var(--font-serif);
  font-size: 1.7rem;
  font-weight: 500;
  margin: 0 0 var(--space-2);
  letter-spacing: -0.01em;
}
.auth-form-header .subtitle {
  color: var(--muted-fg);
  font-size: 0.94rem;
  margin: 0;
}

.auth-error-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: 10px 14px;
  margin-bottom: var(--space-4);
  color: var(--danger);
  font-size: 0.86rem;
  text-align: center;
}
.auth-error-banner::before {
  content: "⚠";
  font-size: 1rem;
  line-height: 1;
  flex: none;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: var(--space-4);
}
.auth-field label {
  font-family: var(--font-sans);
  font-size: 0.86rem;
  font-weight: 500;
  color: var(--fg);
  letter-spacing: 0;
  text-transform: none;
}
.auth-field input,
.auth-field select {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--fg);
  font-family: var(--font-sans);
  font-size: 0.94rem;
  transition: border-color .1s, box-shadow .1s;
}
.auth-field input:focus,
.auth-field select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.auth-field--password { position: relative; }
.auth-field--password input { padding-right: 44px; }
.auth-field--password .pwd-toggle {
  position: absolute;
  right: 6px;
  bottom: 6px;
  width: 34px;
  height: 34px;
  border: none;
  background: transparent;
  color: var(--muted-fg);
  cursor: pointer;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
}
.auth-field--password .pwd-toggle:hover {
  color: var(--fg);
  background: var(--surface-2);
}

.auth-forgot {
  text-align: right;
  margin: calc(var(--space-1) * -1) 0 var(--space-4);
  font-size: 0.86rem;
  color: var(--muted-fg);
}
.auth-forgot a { color: var(--accent); }

.auth-btn-primary {
  display: block;
  width: 100%;
  padding: 12px 16px;
  background: var(--accent);
  border: 1px solid var(--accent);
  color: var(--accent-fg);
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background .1s, border-color .1s;
  text-align: center;
  text-decoration: none;
}
.auth-btn-primary:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
  color: var(--accent-fg);
}

.auth-divider {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin: var(--space-5) 0;
  color: var(--muted-fg);
  font-size: 0.82rem;
}
.auth-divider::before,
.auth-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border);
}

.auth-btn-outline {
  display: block;
  width: 100%;
  padding: 11px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--fg);
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
  font-size: 0.94rem;
  font-weight: 500;
  text-align: center;
  cursor: pointer;
  transition: background .1s;
  text-decoration: none;
}
.auth-btn-outline:hover {
  background: var(--surface-2);
  color: var(--fg);
}

.auth-legal {
  margin-top: var(--space-5);
  text-align: center;
  font-size: 0.78rem;
  color: var(--muted-fg);
  line-height: 1.5;
}
.auth-legal a { color: var(--fg); text-decoration: underline; }

.auth-field-error {
  color: var(--danger);
  font-size: 0.78rem;
  margin-top: 4px;
}

.form-section {
  border: none;
  padding: 0;
  margin: 0 0 var(--space-5);
}
.form-section legend {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted-fg);
  margin-bottom: var(--space-3);
  padding: 0;
}

@media (max-width: 640px) {
  .auth-form-card { padding: var(--space-5); }
  .auth-form-header h1 { font-size: 1.45rem; }
}
```

Run the two verification commands.

### A1.2 Replace `church/templates/auth/login.html`

Overwrite the file completely:

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sign in · Harpr</title>
  <link rel="icon" type="image/svg+xml" href="{% static 'favicon.svg' %}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
  <script>
    (function () {
      var theme = localStorage.getItem("harpr-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      document.documentElement.setAttribute("data-theme", theme);
    })();
  </script>
</head>
<body class="auth-page">

  <header class="auth-topbar">
    <div class="auth-topbar-left">
      <div class="auth-topbar-mark" aria-hidden="true">H</div>
      <div class="auth-topbar-brand">
        <strong>Harpr</strong>
        <small>Church programmes</small>
      </div>
    </div>
    <div class="auth-topbar-actions">
      <button type="button" class="icon-btn" id="theme-toggle" aria-label="Toggle theme">◐</button>
      <a href="{% url 'home' %}">← Back to home</a>
    </div>
  </header>

  <main class="auth-center">
    <div class="auth-form-card">
      <div class="auth-form-header">
        <h1>Welcome back!</h1>
        <p class="subtitle">Log in to your Harpr account</p>
      </div>

      {% if form.non_field_errors %}
        <div class="auth-error-banner" role="alert">
          {{ form.non_field_errors.0 }}
        </div>
      {% elif form.errors %}
        <div class="auth-error-banner" role="alert">
          Incorrect username or password. Please check and try again.
        </div>
      {% endif %}

      <form method="post">
        {% csrf_token %}
        <input type="hidden" name="next" value="{{ next }}">

        <div class="auth-field">
          <label for="{{ form.username.id_for_label }}">Username</label>
          {{ form.username }}
        </div>

        <div class="auth-field auth-field--password">
          <label for="{{ form.password.id_for_label }}">Password</label>
          {{ form.password }}
          <button type="button" class="pwd-toggle" data-pwd-toggle aria-label="Show password">👁</button>
        </div>

        <div class="auth-forgot">
          <a href="{% url 'password_reset' %}">Forgot your password?</a>
        </div>

        <button type="submit" class="auth-btn-primary">Log in</button>
      </form>

      <div class="auth-divider">New to Harpr?</div>
      <a href="{% url 'church_signup' %}" class="auth-btn-outline">Create a church account</a>

      <p class="auth-legal">
        By continuing, you acknowledge that you understand and agree to the
        <a href="{% url 'terms' %}">Terms &amp; Conditions</a> and
        <a href="{% url 'privacy' %}">Privacy Policy</a>.
      </p>
    </div>
  </main>

  <script>
    (function () {
      var toggle = document.getElementById("theme-toggle");
      if (toggle) toggle.addEventListener("click", function () {
        var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("harpr-theme", next);
      });
      document.querySelectorAll("[data-pwd-toggle]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var input = btn.parentNode.querySelector("input");
          if (!input) return;
          var isPwd = input.type === "password";
          input.type = isPwd ? "text" : "password";
          btn.textContent = isPwd ? "🙈" : "👁";
        });
      });
    })();
  </script>
</body>
</html>
```

### A1.3 Add Terms and Privacy views

In `church/views/public_views.py`, add at the very bottom:

```
def terms(request):
    return render(request, "public/terms.html")

def privacy(request):
    return render(request, "public/privacy.html")
```

### A1.4 Add URLs for Terms and Privacy

In `church/urls.py`, add these two lines inside `urlpatterns`, right
after the `home` path:

```
    path("terms/", public_views.terms, name="terms"),
    path("privacy/", public_views.privacy, name="privacy"),
```

### A1.5 Create `templates/public/terms.html`

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Terms &amp; Conditions · Harpr</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
</head>
<body class="public-body">
  <main class="public-shell">
    <header class="public-head">
      <div>
        <p class="eyebrow">Legal</p>
        <h1>Terms &amp; Conditions</h1>
      </div>
      <a class="btn btn-ghost" href="{% url 'home' %}">← Back to home</a>
    </header>
    <section class="public-card">
      <p><strong>Status: In development.</strong></p>
      <p>This page is a placeholder. The full terms and conditions will be published before Harpr is released for general use.</p>
      <p>Harpr is currently a final-year academic project. It is provided as-is for evaluation and demonstration purposes.</p>
    </section>
  </main>
</body>
</html>
```

### A1.6 Create `templates/public/privacy.html`

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Privacy Policy · Harpr</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
</head>
<body class="public-body">
  <main class="public-shell">
    <header class="public-head">
      <div>
        <p class="eyebrow">Legal</p>
        <h1>Privacy Policy</h1>
      </div>
      <a class="btn btn-ghost" href="{% url 'home' %}">← Back to home</a>
    </header>
    <section class="public-card">
      <p><strong>Status: In development.</strong></p>
      <p>Harpr stores only the information needed to plan church programmes: names, email addresses, phone numbers, roles, and schedules. No data is sold or shared with third parties.</p>
      <p>A complete privacy policy, aligned with Zambia's Data Protection Act 2021, will be published before Harpr is released.</p>
    </section>
  </main>
</body>
</html>
```

### A1.7 Replace the four password reset templates

The active password reset templates live in `templates/auth/`.
Overwrite the four active files there.

**`templates/auth/password_reset_form.html`:**

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Reset password · Harpr</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
  <script>
    (function () {
      var theme = localStorage.getItem("harpr-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      document.documentElement.setAttribute("data-theme", theme);
    })();
  </script>
</head>
<body class="auth-page">
  <header class="auth-topbar">
    <div class="auth-topbar-left">
      <div class="auth-topbar-mark" aria-hidden="true">H</div>
      <div class="auth-topbar-brand"><strong>Harpr</strong><small>Church programmes</small></div>
    </div>
    <div class="auth-topbar-actions">
      <button type="button" class="icon-btn" id="theme-toggle" aria-label="Toggle theme">◐</button>
      <a href="{% url 'home' %}">← Back to home</a>
    </div>
  </header>
  <main class="auth-center">
    <div class="auth-form-card">
      <div class="auth-form-header">
        <h1>Reset your password</h1>
        <p class="subtitle">Enter your email and we'll send a link to set a new password.</p>
      </div>
      <form method="post">
        {% csrf_token %}
        <div class="auth-field">
          <label for="id_email">Email</label>
          <input type="email" name="email" id="id_email" required autofocus>
        </div>
        <button type="submit" class="auth-btn-primary">Send reset link</button>
      </form>
      <p class="auth-legal"><a href="{% url 'login' %}">Back to sign in</a></p>
    </div>
  </main>
  <script>
    (function () {
      var toggle = document.getElementById("theme-toggle");
      if (toggle) toggle.addEventListener("click", function () {
        var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("harpr-theme", next);
      });
    })();
  </script>
</body>
</html>
```

**`templates/auth/password_reset_done.html`:**

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Check your email · Harpr</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
</head>
<body class="auth-page">
  <header class="auth-topbar">
    <div class="auth-topbar-left">
      <div class="auth-topbar-mark" aria-hidden="true">H</div>
      <div class="auth-topbar-brand"><strong>Harpr</strong><small>Church programmes</small></div>
    </div>
    <div class="auth-topbar-actions">
      <a href="{% url 'home' %}">← Back to home</a>
    </div>
  </header>
  <main class="auth-center">
    <div class="auth-form-card">
      <div class="auth-form-header">
        <h1>Check your email</h1>
        <p class="subtitle">If an account exists with that email, we've sent a password reset link.</p>
      </div>
      <a href="{% url 'login' %}" class="auth-btn-primary">Back to sign in</a>
    </div>
  </main>
</body>
</html>
```

**`templates/auth/password_reset_confirm.html`:**

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Set a new password · Harpr</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
</head>
<body class="auth-page">
  <header class="auth-topbar">
    <div class="auth-topbar-left">
      <div class="auth-topbar-mark" aria-hidden="true">H</div>
      <div class="auth-topbar-brand"><strong>Harpr</strong><small>Church programmes</small></div>
    </div>
    <div class="auth-topbar-actions">
      <a href="{% url 'home' %}">← Back to home</a>
    </div>
  </header>
  <main class="auth-center">
    <div class="auth-form-card">
      <div class="auth-form-header">
        <h1>Set a new password</h1>
      </div>
      {% if validlink %}
        <form method="post">
          {% csrf_token %}
          <div class="auth-field auth-field--password">
            <label for="id_new_password1">New password</label>
            {{ form.new_password1 }}
            <button type="button" class="pwd-toggle" data-pwd-toggle aria-label="Show password">👁</button>
          </div>
          <div class="auth-field auth-field--password">
            <label for="id_new_password2">Confirm new password</label>
            {{ form.new_password2 }}
            <button type="button" class="pwd-toggle" data-pwd-toggle aria-label="Show password">👁</button>
          </div>
          {% if form.errors %}
            <div class="auth-error-banner" role="alert">
              Passwords do not match or are too short.
            </div>
          {% endif %}
          <button type="submit" class="auth-btn-primary">Save new password</button>
        </form>
      {% else %}
        <div class="auth-error-banner" role="alert">
          This reset link is invalid or has already been used.
        </div>
        <a href="{% url 'password_reset' %}" class="auth-btn-primary">Request a new link</a>
      {% endif %}
    </div>
  </main>
  <script>
    (function () {
      document.querySelectorAll("[data-pwd-toggle]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var input = btn.parentNode.querySelector("input");
          if (!input) return;
          var isPwd = input.type === "password";
          input.type = isPwd ? "text" : "password";
          btn.textContent = isPwd ? "🙈" : "👁";
        });
      });
    })();
  </script>
</body>
</html>
```

**`templates/auth/password_reset_complete.html`:**

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Password reset · Harpr</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
</head>
<body class="auth-page">
  <header class="auth-topbar">
    <div class="auth-topbar-left">
      <div class="auth-topbar-mark" aria-hidden="true">H</div>
      <div class="auth-topbar-brand"><strong>Harpr</strong><small>Church programmes</small></div>
    </div>
    <div class="auth-topbar-actions">
      <a href="{% url 'home' %}">← Back to home</a>
    </div>
  </header>
  <main class="auth-center">
    <div class="auth-form-card">
      <div class="auth-form-header">
        <h1>Password reset complete</h1>
        <p class="subtitle">You can now sign in with your new password.</p>
      </div>
      <a href="{% url 'login' %}" class="auth-btn-primary">Sign in</a>
    </div>
  </main>
</body>
</html>
```

### A1.8 Replace `templates/signup/church_signup.html`

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Create a church account · Harpr</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
  <script>
    (function () {
      var theme = localStorage.getItem("harpr-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      document.documentElement.setAttribute("data-theme", theme);
    })();
  </script>
</head>
<body class="auth-page">
  <header class="auth-topbar">
    <div class="auth-topbar-left">
      <div class="auth-topbar-mark" aria-hidden="true">H</div>
      <div class="auth-topbar-brand"><strong>Harpr</strong><small>Church programmes</small></div>
    </div>
    <div class="auth-topbar-actions">
      <button type="button" class="icon-btn" id="theme-toggle" aria-label="Toggle theme">◐</button>
      <a href="{% url 'home' %}">← Back to home</a>
    </div>
  </header>

  <main class="auth-center">
    <div class="auth-form-card auth-form-card--wide">
      <div class="auth-form-header">
        <h1>Set up your church</h1>
        <p class="subtitle">You'll be the administrator and can invite department heads afterwards.</p>
      </div>

      {% if form.non_field_errors %}
        <div class="auth-error-banner" role="alert">{{ form.non_field_errors.0 }}</div>
      {% endif %}

      <form method="post">
        {% csrf_token %}

        <fieldset class="form-section">
          <legend>Your church</legend>

          <div class="auth-field">
            <label for="{{ form.church_name.id_for_label }}">Church name</label>
            {{ form.church_name }}
            {% if form.church_name.errors %}<div class="auth-field-error">{{ form.church_name.errors.0 }}</div>{% endif %}
          </div>

          <div class="auth-field">
            <label for="{{ form.church_slug.id_for_label }}">Church URL</label>
            {{ form.church_slug }}
            <small class="muted">Becomes /c/<em>your-slug</em>/ — lowercase letters and hyphens.</small>
            {% if form.church_slug.errors %}<div class="auth-field-error">{{ form.church_slug.errors.0 }}</div>{% endif %}
          </div>

          <div class="auth-field">
            <label for="{{ form.worship_day.id_for_label }}">Main worship day</label>
            {{ form.worship_day }}
          </div>

          <div class="auth-field">
            <label for="{{ form.church_address.id_for_label }}">Address (optional)</label>
            {{ form.church_address }}
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>Your administrator account</legend>

          <div class="auth-field">
            <label for="{{ form.coordinator_username.id_for_label }}">Username</label>
            {{ form.coordinator_username }}
            {% if form.coordinator_username.errors %}<div class="auth-field-error">{{ form.coordinator_username.errors.0 }}</div>{% endif %}
          </div>

          <div class="auth-field">
            <label for="{{ form.coordinator_email.id_for_label }}">Email</label>
            {{ form.coordinator_email }}
            {% if form.coordinator_email.errors %}<div class="auth-field-error">{{ form.coordinator_email.errors.0 }}</div>{% endif %}
          </div>

          <div class="auth-field">
            <label for="{{ form.coordinator_first_name.id_for_label }}">First name</label>
            {{ form.coordinator_first_name }}
          </div>

          <div class="auth-field">
            <label for="{{ form.coordinator_last_name.id_for_label }}">Last name</label>
            {{ form.coordinator_last_name }}
          </div>

          <div class="auth-field auth-field--password">
            <label for="{{ form.password1.id_for_label }}">Password</label>
            {{ form.password1 }}
            <button type="button" class="pwd-toggle" data-pwd-toggle aria-label="Show password">👁</button>
            {% if form.password1.errors %}<div class="auth-field-error">{{ form.password1.errors.0 }}</div>{% endif %}
          </div>

          <div class="auth-field auth-field--password">
            <label for="{{ form.password2.id_for_label }}">Confirm password</label>
            {{ form.password2 }}
            <button type="button" class="pwd-toggle" data-pwd-toggle aria-label="Show password">👁</button>
            {% if form.password2.errors %}<div class="auth-field-error">{{ form.password2.errors.0 }}</div>{% endif %}
          </div>
        </fieldset>

        <button type="submit" class="auth-btn-primary">Create church account</button>
      </form>

      <p class="auth-legal">
        Already have an account? <a href="{% url 'login' %}">Sign in</a>.<br>
        By continuing, you acknowledge that you understand and agree to the
        <a href="{% url 'terms' %}">Terms &amp; Conditions</a> and
        <a href="{% url 'privacy' %}">Privacy Policy</a>.
      </p>
    </div>
  </main>

  <script>
    (function () {
      var toggle = document.getElementById("theme-toggle");
      if (toggle) toggle.addEventListener("click", function () {
        var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("harpr-theme", next);
      });
      document.querySelectorAll("[data-pwd-toggle]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var input = btn.parentNode.querySelector("input");
          if (!input) return;
          var isPwd = input.type === "password";
          input.type = isPwd ? "text" : "password";
          btn.textContent = isPwd ? "🙈" : "👁";
        });
      });
    })();
  </script>
</body>
</html>
```

### A1.9 Replace `templates/signup/accept_invitation.html`

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Accept invitation · Harpr</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
  <script>
    (function () {
      var theme = localStorage.getItem("harpr-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      document.documentElement.setAttribute("data-theme", theme);
    })();
  </script>
</head>
<body class="auth-page">
  <header class="auth-topbar">
    <div class="auth-topbar-left">
      <div class="auth-topbar-mark" aria-hidden="true">H</div>
      <div class="auth-topbar-brand"><strong>Harpr</strong><small>Church programmes</small></div>
    </div>
    <div class="auth-topbar-actions">
      <button type="button" class="icon-btn" id="theme-toggle" aria-label="Toggle theme">◐</button>
      <a href="{% url 'home' %}">← Back to home</a>
    </div>
  </header>

  <main class="auth-center">
    <div class="auth-form-card">
      <div class="auth-form-header">
        <h1>Join {{ invitation.church.name }}</h1>
        <p class="subtitle">
          You were invited as a {{ invitation.get_role_display }}{% if invitation.department %} for {{ invitation.department.name }}{% endif %}.
        </p>
      </div>

      {% if error %}
        <div class="auth-error-banner" role="alert">{{ error }}</div>
      {% endif %}

      <form method="post">
        {% csrf_token %}

        <div class="auth-field">
          <label for="first_name">First name</label>
          <input name="first_name" id="first_name" autocomplete="given-name" required>
        </div>

        <div class="auth-field">
          <label for="last_name">Last name</label>
          <input name="last_name" id="last_name" autocomplete="family-name" required>
        </div>

        <div class="auth-field">
          <label for="phone">Phone number</label>
          <input name="phone" id="phone" type="tel" autocomplete="tel" placeholder="+260 ..." required>
        </div>

        <div class="auth-field">
          <label for="username">Username</label>
          <input name="username" id="username" required autocomplete="username">
        </div>

        <div class="auth-field auth-field--password">
          <label for="password1">Password</label>
          <input type="password" name="password1" id="password1" required autocomplete="new-password">
          <button type="button" class="pwd-toggle" data-pwd-toggle aria-label="Show password">👁</button>
        </div>

        <div class="auth-field auth-field--password">
          <label for="password2">Confirm password</label>
          <input type="password" name="password2" id="password2" required autocomplete="new-password">
          <button type="button" class="pwd-toggle" data-pwd-toggle aria-label="Show password">👁</button>
        </div>

        <button type="submit" class="auth-btn-primary">Accept invitation</button>
      </form>

      <p class="auth-legal">
        By continuing, you acknowledge that you understand and agree to the
        <a href="{% url 'terms' %}">Terms &amp; Conditions</a> and
        <a href="{% url 'privacy' %}">Privacy Policy</a>.
      </p>
    </div>
  </main>

  <script>
    (function () {
      var toggle = document.getElementById("theme-toggle");
      if (toggle) toggle.addEventListener("click", function () {
        var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("harpr-theme", next);
      });
      document.querySelectorAll("[data-pwd-toggle]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var input = btn.parentNode.querySelector("input");
          if (!input) return;
          var isPwd = input.type === "password";
          input.type = isPwd ? "text" : "password";
          btn.textContent = isPwd ? "🙈" : "👁";
        });
      });
    })();
  </script>
</body>
</html>
```

### A1.10 Replace `templates/signup/invitation_invalid.html`

```
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Invitation unavailable · Harpr</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/harpr.css' %}">
</head>
<body class="auth-page">
  <header class="auth-topbar">
    <div class="auth-topbar-left">
      <div class="auth-topbar-mark" aria-hidden="true">H</div>
      <div class="auth-topbar-brand"><strong>Harpr</strong><small>Church programmes</small></div>
    </div>
    <div class="auth-topbar-actions">
      <a href="{% url 'home' %}">← Back to home</a>
    </div>
  </header>
  <main class="auth-center">
    <div class="auth-form-card">
      {% if already_accepted %}
        <div class="auth-form-header">
          <h1>You already accepted this</h1>
          <p class="subtitle">This invitation has already been used to create an account.</p>
        </div>
        <p class="muted" style="text-align:center;">
          If you're having trouble signing in, use the password reset link below, or contact your church administrator.
        </p>
        <a href="{% url 'password_reset' %}" class="auth-btn-primary">Reset your password</a>
        <div class="auth-divider">or</div>
        <a href="{% url 'login' %}" class="auth-btn-outline">Back to sign in</a>
      {% else %}
        <div class="auth-form-header">
          <h1>This invitation has expired</h1>
          <p class="subtitle">The link is either too old or has already been used.</p>
        </div>
        <p class="muted" style="text-align:center;">
          Ask your church administrator to send you a new invitation.
        </p>
        <a href="{% url 'login' %}" class="auth-btn-primary">Back to sign in</a>
      {% endif %}
    </div>
  </main>
</body>
</html>
```

### A1.11 Replace `church/views/invitation_views.py`

```
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from church.models import Invitation, Membership, Person

def accept_invitation(request, token):
    invitation = get_object_or_404(Invitation, token=token)

    # Already-accepted state: the invitation has been used before.
    if invitation.accepted_at:
        return render(
            request,
            "signup/invitation_invalid.html",
            {"invitation": invitation, "already_accepted": True},
        )

    # Expired or otherwise invalid state.
    if not invitation.is_valid():
        return render(
            request,
            "signup/invitation_invalid.html",
            {"invitation": invitation, "already_accepted": False},
        )

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()

        error = None
        if not username:
            error = "Username is required."
        elif not first_name:
            error = "First name is required."
        elif not last_name:
            error = "Last name is required."
        elif not phone:
            error = "Phone number is required."
        elif User.objects.filter(username=username).exists():
            error = "That username is taken."
        elif password1 != password2:
            error = "The two passwords don't match."
        elif len(password1) < 8:
            error = "Password must be at least 8 characters."

        if error:
            return render(
                request,
                "signup/accept_invitation.html",
                {"invitation": invitation, "error": error},
            )

        user = User.objects.create_user(
            username=username,
            email=invitation.email,
            first_name=first_name,
            last_name=last_name,
            password=password1,
        )

        Membership.objects.create(
            user=user,
            church=invitation.church,
            role=invitation.role,
            department=invitation.department,
            invited_by=invitation.invited_by,
        )

        # Record the member as a Person so the phone number is queryable.
        full_name = f"{first_name} {last_name}".strip()
        Person.objects.create(
            church=invitation.church,
            name=full_name or username,
            phone=phone,
            email=invitation.email,
            user=user,
        )

        invitation.accepted_at = timezone.now()
        invitation.save()

        login(request, user)
        return redirect("home")

    return render(
        request,
        "signup/accept_invitation.html",
        {"invitation": invitation},
    )
```

### A1.12 Final verification for part 1

Run:

```
python manage.py check
python manage.py test church
```

Both must pass. Then start the dev server and walk through:

1. `/accounts/login/` — centered card, "Welcome back!", red error banner with ⚠ icon on wrong password, eye toggle works, "Back to home" top-right, theme toggle top-right.
2. `/signup/` — same shell, wider card, section legends, eye toggles work.
3. `/terms/` and `/privacy/` — both render.
4. `/accounts/password-reset/` — centered card.
5. Manually add an `Invitation` row in the Django admin for an existing church, visit `/invite/<token>/`, fill in first name, last name, phone, username, password, submit. Verify the `Membership` and `Person` rows were created and the user is logged in.
6. Visit `/invite/<same-token>/` again — should show the "You already accepted this" page.

If all six pass, part 1 is complete.

**STOP. Do not read part 2 of this spec until instructed.**

---

## End of part 1

Report completion status with:

- Output of `python manage.py check`
- Output of `python manage.py test church`
- A one-line summary of each of the six manual checks above

Wait for instruction before proceeding to part 2.