# Harpr — MD A, Part 4b: 24-hour sweep, mobile CSS, cleanup, final push

**This is part 4b of 4b — the final part of MD A.**

- Parts 1, 2, 2b, 3 (applied): Sections A0.5 → A6.8
- Part 4a (applied): Sections P4.1 → P4.6
- **Part 4b (this file):** Sections P4.7 → P4.10

**Read this entire file before touching code. Do not re-apply anything from parts 1, 2, 2b, 3, or 4a.**

---

## Before you start

**Repo state:** parts 1 through 4a are applied and green. Two
migrations were added in part 4a (`announcement_tighten` and
`membership_deactivated_at`). Nothing is committed yet.
`origin/main` is at `165c305`.

**Environment:**

```
cd /root/harpr && . .venv/bin/activate
```

**Verification after each section:**

```
python manage.py check
python manage.py test church
```

Both must pass before continuing.

---

## Section P4.7 — Real 24-hour time sweep

The app should display times as `18:00`, not `6:00 PM`. This section
finds and fixes every AM/PM format string in the templates and forms.

### P4.7.1 Find every time-rendering location

Run:

```
grep -rn 'time:"' church/templates/ templates/
grep -rn "TimeInput\|%H:%M\|%I:%M" church/forms.py
```

The first command shows every Django `time` filter. The second shows
every time widget format string.

### P4.7.2 Fix any AM/PM template formats

If the first command returned any of these patterns, replace them:

| Find ↕▾ | Replace with ↕▾ |
|---|---|
| −`time:"g:i A"` | `time:"H:i"` |
| `time:"h:i A"` | `time:"H:i"` |
| `time:"H:i A"` | `time:"H:i"` |
| `time:"P"` | `time:"H:i"` |
⚙

Any format ending in `A` or `a` is AM/PM. `H:i` is 24-hour.

### P4.7.3 Fix any AM/PM form widgets

In `church/forms.py`, if the second command shows any of these:

- `format="%I:%M %p"`
- `format="%I:%M%p"`
- `format="%-I:%M %p"`

Replace each with `format="%H:%M"`.

Also check that any `TimeInput` widget does not pass a `strftime`-based
format that includes `%p`.

### P4.7.4 Verify

Run the two verification commands.

Then start the dev server and visit every page that displays a time:

- `/dashboard/`
- `/services/`
- `/services/<pk>/` (any service detail page)
- `/c/grace-covenant/`

Confirm every time shows as `HH:MM`. If any show `AM` or `PM`, stop and
report which page.

### P4.7.5 Report

Note in your final report:

- How many files you changed in this section
- Which templates or form widgets had AM/PM before the change
- Confirmation that all four URLs above show 24-hour times

---

## Section P4.8 — Defensive mobile CSS

Copilot cannot open a browser at 375px, so this section adds a
comprehensive set of rules that make every page type work on a phone.

### P4.8.1 Append to `static/css/harpr.css`

Append at the very bottom of the file:

```
/* ============================================================
   MOBILE — defensive rules for every page type
   ============================================================ */

@media (max-width: 768px) {
  /* Layout: sidebar collapses to a top bar */
  .layout {
    grid-template-columns: 1fr;
    display: block;
  }
  .sidebar {
    position: static;
    height: auto;
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border);
    padding: var(--space-4);
  }
  .sidenav {
    flex-direction: row;
    flex-wrap: wrap;
    overflow-x: auto;
    gap: var(--space-1);
    margin: 0;
  }
  .navlink {
    padding: 6px 12px;
    font-size: 0.82rem;
    white-space: nowrap;
  }
  .sidebar-footer {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-top: var(--space-3);
  }
  .main {
    padding: var(--space-4);
  }

  /* Page head: stack buttons under the title */
  .page-head {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
    padding-bottom: var(--space-3);
  }
  .page-head h1 {
    font-size: 1.4rem;
  }
  .page-head .button-row {
    display: flex;
    gap: var(--space-2);
    flex-wrap: wrap;
  }
  .page-head .button-row .btn {
    flex: 1 1 auto;
  }

  /* Week grid: horizontal scroll */
  .week-grid {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
    border-radius: var(--radius);
  }
  .week-col {
    flex: 0 0 200px;
    scroll-snap-align: start;
  }

  /* Stat grid: two per row */
  .stat-grid {
    grid-template-columns: 1fr 1fr;
  }
  .stat-card {
    padding: var(--space-3);
  }
  .stat-value {
    font-size: 1.4rem;
  }
}

@media (max-width: 640px) {
  /* Tables: horizontal scroll with tightened padding */
  .table-wrap {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    margin: 0 calc(var(--space-3) * -1);
    padding: 0 var(--space-3);
  }
  .data-table,
  .public-table {
    font-size: 0.78rem;
    min-width: 540px;
  }
  .data-table th,
  .data-table td,
  .public-table th,
  .public-table td {
    padding: 6px 8px;
    white-space: nowrap;
  }
  .data-table th,
  .public-table th {
    font-size: 0.66rem;
  }

  /* Forms: single column, larger touch targets */
  .form-row.two-up {
    grid-template-columns: 1fr;
    gap: var(--space-2);
  }
  .form-row input,
  .form-row select,
  .form-row textarea {
    font-size: 16px; /* prevents iOS auto-zoom on focus */
    padding: 10px 12px;
  }

  /* Row actions: wrap and stay readable */
  .row-actions-inline {
    flex-wrap: wrap;
    gap: 4px;
  }
  .row-actions-inline .btn-small {
    padding: 4px 8px;
    font-size: 0.72rem;
  }

  /* Modal: bottom sheet on mobile */
  .modal-backdrop {
    align-items: flex-end;
    padding: 0;
  }
  .modal {
    max-width: none;
    margin: 0;
    border-radius: var(--radius) var(--radius) 0 0;
    max-height: 92vh;
  }
  .modal-head {
    padding: var(--space-3) var(--space-4);
  }
  .modal-body {
    padding: var(--space-4);
  }
  .modal .form-actions {
    flex-direction: column-reverse;
    gap: var(--space-2);
  }
  .modal .form-actions .btn {
    width: 100%;
    padding: 12px;
  }

  /* Buttons: comfortable touch size */
  .btn {
    padding: 10px 16px;
    font-size: 0.86rem;
  }
  .btn-small {
    padding: 6px 10px;
    font-size: 0.78rem;
  }

  /* Public shell: full width, tighter padding */
  .public-shell {
    padding: var(--space-4) var(--space-3) var(--space-6);
  }
  .public-head {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
  }
  .public-head h1 {
    font-size: 1.5rem;
  }
  .public-card {
    padding: var(--space-4) var(--space-3);
  }
  .public-table {
    font-size: 0.8rem;
  }
  .public-links {
    text-align: left;
  }

  /* Auth cards: full width on mobile */
  .auth-page {
    padding: var(--space-3);
  }
  .auth-form-card,
  .auth-form-card--wide {
    max-width: none;
    padding: var(--space-5) var(--space-4);
  }
  .auth-form-header h1 {
    font-size: 1.4rem;
  }
  .auth-topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
  }
  .auth-topbar-actions {
    width: 100%;
    justify-content: space-between;
  }

  /* Footer: stack contact lines */
  .public-footer .footer-contacts {
    flex-direction: column;
    gap: var(--space-2);
  }

  /* Notifications dropdown: full width */
  .notif-dropdown {
    position: fixed;
    left: var(--space-3);
    right: var(--space-3);
    top: 60px;
    width: auto;
    max-width: none;
  }

  /* Section labels */
  .section-label {
    font-size: 0.68rem;
  }
}

@media (max-width: 400px) {
  /* Very small phones */
  .stat-grid {
    grid-template-columns: 1fr;
  }
  .page-head h1 {
    font-size: 1.25rem;
  }
  .btn {
    font-size: 0.8rem;
    padding: 9px 14px;
  }
}
```

### P4.8.2 Verify

Run the two verification commands.

Count the media blocks:

```
grep -c "@media" static/css/harpr.css
```

The number should be greater than 6. Report it.

### P4.8.3 Report

Note in your final report:

> P4.8 is a defensive baseline only. The user must still open the site
> on a phone or in a browser at 375px to confirm the pages look right.
> The week grid horizontal scroll and the members table overflow are
> the two areas most likely to need follow-up tuning.

---

## Section P4.9 — Clean up junk files

### P4.9.1 Remove the Zone.Identifier files

```
rm -f "HARPR_A_part1.md:Zone.Identifier"
rm -f "HARPR_A_part2.md:Zone.Identifier"
rm -f "HARPR_A_part2b.md:Zone.Identifier"
rm -f "HARPR_A_part3.md:Zone.Identifier"
rm -f "HARPR_A_part4.md:Zone.Identifier"
rm -f "HARPR_A_part4a.md:Zone.Identifier"
rm -f "HARPR_A_part4b.md:Zone.Identifier"
```

### P4.9.2 Add to `.gitignore`

Open `.gitignore` and add these two lines at the very bottom:

```
# Windows download metadata
*:Zone.Identifier
```

### P4.9.3 Remove the stale spec files

Two files in the repo root are obsolete. Remove them so they cannot be
committed:

```
git rm -f HARPR_MD_A_v2.md 2>/dev/null || rm -f HARPR_MD_A_v2.md
git rm -f HARPR_MD_A_TRUNCATED_DO_NOT_USE.md 2>/dev/null || rm -f HARPR_MD_A_TRUNCATED_DO_NOT_USE.md
```

### P4.9.4 Remove the truncated part 4

If `HARPR_A_part4.md` still exists in the repo (the truncated version
from before part 4a and 4b were written), remove it:

```
rm -f HARPR_A_part4.md
rm -f "HARPR_A_part4.md:Zone.Identifier"
```

### P4.9.5 Verify

Run the two verification commands.

---

## Section P4.10 — Final commit and push

### P4.10.1 Pre-flight check

Run all three:

```
python manage.py check
python manage.py test church
python manage.py makemigrations --check --dry-run
```

The third must print "No changes detected." If it reports pending
migrations, run `makemigrations`, apply with `migrate`, run the tests
again, and include the new migration in the commit.

### P4.10.2 Commit and push

```
cd /root/harpr
git add -A
git status --short
```

Review the output. It should show:

- Every modified file from parts 1–4b
- The three new migrations (footer, announcement_tighten, membership_deactivated_at)
- New templates: `_public_footer.html`, `terms.html`, `privacy.html`
- The six spec files as untracked additions:

- `HARPR_A_part1.md`
- `HARPR_A_part2.md`
- `HARPR_A_part2b.md`
- `HARPR_A_part3.md`
- `HARPR_A_part4a.md`
- `HARPR_A_part4b.md`
- `.gitignore` modified
- `HARPR_MD_A_v2.md` and `HARPR_MD_A_TRUNCATED_DO_NOT_USE.md` removed
- `HARPR_A_part4.md` removed if it was there

**If anything looks wrong — a file you did not expect, or a file
missing that should be there — stop and report the full `git status
--short` output before committing.**

If it looks correct, commit and push:

```
git commit -m "MD A v2: login redesign, members table, announcement lifecycle, footer, mobile fixes"
git push origin main
```

Report the **full output of `git push origin main`**.

### P4.10.3 Remove the spec files and push again

```
git rm HARPR_A_part1.md
git rm HARPR_A_part2.md
git rm HARPR_A_part2b.md
git rm HARPR_A_part3.md
git rm HARPR_A_part4a.md
git rm HARPR_A_part4b.md
git commit -m "Remove applied spec files"
git push origin main
```

Report the full output of that second push.

If any command fails, stop and report the exact error.

---

## End of part 4b — MD A is complete

Report in one message:

- Output of `python manage.py check`
- Output of `python manage.py test church`
- Output of `python manage.py makemigrations --check --dry-run`
- Output of both `git push` commands
- Number of `@media` blocks in `harpr.css`
- Which files P4.7 changed for the 24-hour sweep
- Confirmation that the PDF renders announcements on page 2
- Confirmation that clicking "New announcement" opens a modal
- Confirmation that clicking "New service" opens a modal
- Confirmation that the "Show all members" toggle reveals backdated
deactivated members
- A one-line note on any section you could not apply, with the exact error

Do not begin any other work until the user reviews this.