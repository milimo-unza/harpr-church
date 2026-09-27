## Section R6 (continued) — Notification bell CSS

### R6.2 (redo) — Append the CSS to `static/css/harpr.css`

Open `static/css/harpr.css` and append at the very bottom:

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
    right: var(--space-4);
    bottom: var(--space-4);
  }
  .notif-bell--floating .notif-dropdown {
    width: calc(100vw - 32px);
    max-width: 360px;
  }
}
```

### R6.3 — Verify

```
python manage.py check
python manage.py test church
```

Reload any staff page.

1. **Top of the page** — no topbar, no bell icon.
2. **Bottom-right** — if there are unread notifications, a terracotta circular button appears with a badge.
3. **Click it** — the dropdown opens upward from the button.
4. **When there are zero notifications** — the button is completely hidden.

---

## Section R7 — Commit and push

```
cd /root/harpr
python manage.py check
python manage.py test church
python manage.py makemigrations --check --dry-run
```

The third command must print "No changes detected."

```
git add -A
git status --short
```

Review the staged list — it should include `church/templates/church/members.html`, `church/templates/church/dashboard.html`, `church/templates/church/departments.html`, `church/templates/church/announcements.html`, `church/templates/church/base.html`, `church/views/admin_views.py`, `church/urls.py`, `static/css/harpr.css`.

If anything looks wrong, stop and report the full `git status --short` output.

Otherwise:

```
git commit -m "Fix member and department modals, dashboard service modal, announcement form cleanup, floating notification bell"
git push origin main
```

Report the full output of `git push origin main`.

Then remove the spec file:

```
git rm HARPR_fix_round2.md HARPR_round2_tail.md 2>/dev/null || rm -f HARPR_fix_round2.md HARPR_round2_tail.md
git commit -m "Remove applied round 2 spec"
git push origin main
```

Report the output of the second push.

---

## End of round 2

Report in one message:

- Output of `python manage.py check`
- Output of `python manage.py test church`
- Confirmation that "Add member" opens a modal
- Confirmation that "New service" on the dashboard opens a modal
- Confirmation that "New department" opens a modal
- Confirmation that the announcement create modal has no Service dropdown
- Confirmation that the notification bell is a floating button at the bottom right
- Both push outputs