# Harpr — MD A: Login Redesign, Members, Announcements, Landing, Mobile

**Read this whole file before you touch code.** It is calibrated against the
current state of the repo on GitHub (`milimo-unza/harpr-church`, commit
`165c305`). Every path and function name below has been verified against
that code.

After each section, run:

```

python manage.py check
python manage.py test church

```

Both must pass. If a section fails, fix the error and continue. Do not stop
between sections unless you cannot resolve an error in two attempts.

**Stack:** Django 6 · SQLite · Django templates · vanilla JS. No React,
no TypeScript, no bundler.

**Files to leave alone:**
- `church/services/recalculation.py`
- `church/services/qr.py`
- `church/migrations/0001_*` through `0005_*` (only add new migrations)
- `manage.py`, `harpr_church/wsgi.py`, `harpr_church/asgi.py`

**Templates that currently exist and are dead.** The repo has three login
templates. Only one is served. Section A0 deletes the other two:

- `church/templates/auth/login.html` ← served (via `template_name="auth/login.html"`)
- `templates/auth/login.html` (dead — never wired)
- `church/templates/church/auth/login.html` (dead — old, references `cosmos.css`)

---

## Section A0 — Clean up dead template copies and stale CSS

Delete:

```bash
rm -f templates/auth/login.html
rm -f church/templates/church/auth/login.html
rm -f static/css/cosmos.css
rm -f static/css/church.css
```

Confirm nothing references the deleted files:

```
grep -rn "cosmos.css\|church.css" church/templates/ templates/ static/js/ 2>/dev/null
```

Should print nothing. If it prints something, stop and report the line.

```
python manage.py check
python manage.py test church
```

Both must pass.

---

## Section A1 — Login, signup, invitation, password reset redesign

The new design is a centered card: brand mark top-left, "Welcome back!"
centered, error banner centered in red above the form, password fields
with a show/hide eye, divider above the "create an account" link. Back
to home and theme toggle in the top-right corner of the page.

### A1.1 Append auth CSS to `static/css/harpr.css`

**Append** this to the end of `static/css/harpr.css`. Do not overwrite
the existing content.

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
.auth-topbar-left { display: flex; align-items: center; gap: var(--space-3); }
.auth-topbar-mark {
  width: 40px; height: 40px;
  border-radius: 10px;
  background: var(--accent);
  color: var(--accent-fg);
  display: inline-flex; align-items: center; justify-content: center;
  font-family: var(--font-serif);
  font-size: 1.35rem;
  font-weight: 600;
}
.auth-topbar-brand { display: flex; flex-direction: column; }
.auth-topbar-brand strong {
  font-family: var(--font-serif);
  font-size: 1.35rem;
  font-weight: 600;
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
.auth-topbar-actions { display: flex; align-items: center; gap: var(--space-2); }
.auth-topbar-actions a {
  font-size: 0.86rem;
  color: var(--muted-fg);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
}
.auth-topbar-actions a:hover { color: var(--fg); background: var(--surface-2); }

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

.auth-form-header { text-align: center; margin-bottom: var(--space-5); }
.auth-form-header h1 {
  font-family: var(--font-serif);
  font-size: 1.7rem;
  font-weight: 600;
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
  width: 34px; height: 34px;
  border: none;
  background: transparent;
  color: var(--muted-fg);
  cursor: pointer;
  border-radius: var(--radius-sm);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 0.95rem;
}
.auth-field--password .pwd-toggle:hover { color: var(--fg); background: var(--surface-2); }

.auth-forgot {
  text-align: right;
  margin: calc(var(--space-1) * -1) 0 var(--space-4);
  font-size: 0.86rem;
  color: var(--muted-fg);
}
.auth-forgot a { color: var(--accent); }

.auth-btn-primary {
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
}
.auth-btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }

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
.auth-btn-outline:hover { background: var(--surface-2); color: var(--fg); }

.auth-legal {
  margin-top: var(--space-5);
  text-align: center;
  font-size: 0.78rem;
  color: var(--muted-fg);
  line-height: 1.5;
}
.auth-legal a { color: var(--fg); text-decoration: underline; }

.auth-field-error { color: var(--danger); font-size: 0.78rem; margin-top: 4px; }

@media (max-width: 640px) {
  .auth-form-card { padding: var(--space-5); }
  .auth-form-header h1 { font-size: 1.45rem; }
}
```

### A1.2 Replace `church/templates/auth/login.html`

**This is the file Django actually serves.** `harpr_church/urls.py` uses
`template_name="auth/login.html"`, and `church/templates/` is discovered
via `APP_DIRS`. Overwrite the file entirely:

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

In `church/views/public_views.py`, add at the bottom:

```
def terms(request):
    return render(request, "public/terms.html")

def privacy(request):
    return render(request, "public/privacy.html")
```

### A1.4 Add URLs

In `church/urls.py`, add:

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
      <div><p class="eyebrow">Legal</p><h1>Terms &amp; Conditions</h1></div>
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
      <div><p class="eyebrow">Legal</p><h1>Privacy Policy</h1></div>
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

### A1.7 Update the password reset templates

Overwrite `templates/auth/password_reset_form.html`:

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
</body>
</html>
```

Overwrite `templates/auth/password_reset_done.html`:

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
      <a href="{% url 'login' %}" class="auth-btn-primary" style="display:block;text-align:center;">Back to sign in</a>
    </div>
  </main>
</body>
</html>
```

Overwrite `templates/auth/password_reset_confirm.html`:

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
          {{ form.as_p }}
          <button type="submit" class="auth-btn-primary">Save new password</button>
        </form>
      {% else %}
        <div class="auth-error-banner" role="alert">
          This reset link is invalid or has already been used.
        </div>
        <a href="{% url 'password_reset' %}" class="auth-btn-primary" style="display:block;text-align:center;">Request a new link</a>
      {% endif %}
    </div>
  </main>
</body>
</html>
```

Overwrite `templates/auth/password_reset_complete.html`:

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
      <a href="{% url 'login' %}" class="auth-btn-primary" style="display:block;text-align:center;">Sign in</a>
    </div>
  </main>
</body>
</html>
```

### A1.8 Update `templates/signup/accept_invitation.html` and `church_signup.html`

Both currently use `auth-body` + `auth-card`. Wrap them the same way as
the login page: use `auth-page`, add the `auth-topbar` with back link
and theme toggle, use `auth-center`, use `auth-form-card` (with `--wide`
for signup), use `auth-form-header` for the title, use `auth-field`
for each input, use `auth-error-banner` for errors, and use
`auth-btn-primary` for the submit. End with an `auth-legal` block that
mentions Terms and Privacy.

The simplest approach: for both files, replace `class="auth-body"` with
`class="auth-page"`, insert the same `auth-topbar` used in the login
template, wrap the card in `<main class="auth-center">`, change
`class="auth-card"` to `class="auth-form-card"`, change
`class="auth-brand"` to `class="auth-form-header"`, replace each
`class="form-row"` with `class="auth-field"`, and replace
`class="btn btn-primary btn-block"` with `class="auth-btn-primary"`.

Add to the end of each, inside the form card:

```
      <p class="auth-legal">
        By continuing, you acknowledge that you understand and agree to the
        <a href="{% url 'terms' %}">Terms &amp; Conditions</a> and
        <a href="{% url 'privacy' %}">Privacy Policy</a>.
      </p>
```

Add the password show/hide toggle to any password input. Add the theme
toggle script to each page, same as in the login template.

### A1.9 Test

```
python manage.py check
python manage.py test church
```

Visit `/accounts/login/`. Centered card, Newsreader heading, terracotta
"Log in" button, legal footer. Try a wrong password — the error banner
should appear centered in red.

Visit `/signup/`. Same shell, wider card.

Visit `/terms/` and `/privacy/`.

---

## Section A2 — Members table: Edit and Deactivate on the same line

### A2.1 Update `member_list` in `church/views/admin_views.py`

Find `member_list` and change it to pass `departments`:

```
@admin_required
def member_list(request):
    memberships = request.church.memberships.select_related(
        "user", "department", "invited_by")
    departments = request.church.departments.all()
    return render(request, "church/members.html", {
        "memberships": memberships,
        "departments": departments,
    })
```

### A2.2 Replace `church/templates/church/members.html`

```
{% extends "church/base.html" %}
{% block title %}Members · Harpr{% endblock %}
{% block content %}
<div class="page-head">
  <div><p class="eyebrow">Access</p><h1>Members</h1></div>
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
        <th scope="col">Active</th>
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
            {% if m.is_active %}<span class="status-badge status-approved">Active</span>
            {% else %}<span class="status-badge status-skipped">Deactivated</span>{% endif %}
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

<div class="modal-backdrop" id="invite-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true">
    <div class="modal-head"><h2>Invite member</h2><button type="button" class="icon-btn modal-close">✕</button></div>
    <div class="modal-body">
      <p class="muted">Enter the person's email and choose their role and department. Harpr will email them an invitation link that expires in 7 days and can only be used once.</p>
      <form method="post" action="{% url 'member_invite' %}">
        {% csrf_token %}
        <div class="form-row"><label for="invite_email">Email</label><input type="email" name="email" id="invite_email" required></div>
        <div class="form-row"><label for="invite_role">Role</label>
          <select name="role" id="invite_role">
            <option value="dept_head">Department Head</option>
            <option value="admin">Administrator</option>
          </select>
        </div>
        <div class="form-row"><label for="invite_department">Department</label>
          <select name="department" id="invite_department">
            <option value="">— None —</option>
            {% for d in departments %}<option value="{{ d.pk }}">{{ d.name }}</option>{% endfor %}
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
    <div class="modal-head"><h2>Edit {{ m.user.username }}</h2><button type="button" class="icon-btn modal-close">✕</button></div>
    <div class="modal-body">
      <p class="muted">Names are set by the member themselves. As administrator you can change their role, department, or deactivate their account.</p>
      <form method="post" action="{% url 'member_edit' m.pk %}">
        {% csrf_token %}
        <div class="form-row"><label>Role</label>
          <select name="role">
            <option value="dept_head" {% if m.role == 'dept_head' %}selected{% endif %}>Department Head</option>
            <option value="admin" {% if m.role == 'admin' %}selected{% endif %}>Administrator</option>
          </select>
        </div>
        <div class="form-row"><label>Department</label>
          <select name="department">
            <option value="">— None —</option>
            {% for d in departments %}<option value="{{ d.pk }}" {% if m.department_id == d.pk %}selected{% endif %}>{{ d.name }}</option>{% endfor %}
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
  <div class="modal" role="dialog" aria-modal="true" style="max-width:440px;">
    <div class="modal-head"><h2>Deactivate member?</h2><button type="button" class="icon-btn modal-close">✕</button></div>
    <div class="modal-body">
      <p>Deactivating <strong>{{ m.user.username }}</strong> will prevent them from logging in. They will receive an email notification. Their historical entries remain in the system.</p>
      <form method="post" action="{% url 'member_deactivate' m.pk %}">
        {% csrf_token %}
        <div class="form-actions">
          <button type="button" class="btn btn-ghost
