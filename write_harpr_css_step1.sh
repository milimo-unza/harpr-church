#!/bin/bash

# Step 1 of 2 — writes the base rules to static/css/harpr.css

# Run from ~/harpr after activating the venv.

set -e
cd ~/harpr

cp static/css/harpr.css static/css/harpr.css.broken-backup 2>/dev/null || true

cat > static/css/harpr.css << 'ENDOFCSS'
/* ============================================================
Harpr — Clean design system
============================================================ */

:root {
--bg: #f7f3ea;
--surface: #fdfbf6;
--surface-2: #efe9dc;
--fg: #2a2419;
--muted-fg: #6f6656;
--border: #ddd4c2;
--hairline: #ece5d5;
--accent: #a85430;
--accent-hover: #8f4526;
--accent-fg: #ffffff;
--accent-soft: rgba(168, 84, 48, 0.08);
--ok: #5a7a44;
--warn: #a87a2a;
--danger: #9e3a2e;
--font-sans: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif;
--font-serif: 'Newsreader', 'Iowan Old Style', Georgia, serif;
--font-mono: 'JetBrains Mono', ui-monospace, Menlo, monospace;
--radius: 6px;
--radius-sm: 4px;
--radius-pill: 999px;
--shadow-sm: 0 1px 1px rgba(60, 40, 20, 0.03);
--shadow-md: 0 2px 4px rgba(60, 40, 20, 0.04);
--shadow-lg: 0 8px 16px rgba(60, 40, 20, 0.06);
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 24px;
--space-6: 32px;
--space-7: 48px;
}

[data-theme="dark"] {
--bg: #17140f;
--surface: #1f1b14;
--surface-2: #2a251b;
--fg: #ece4d4;
--muted-fg: #9a9280;
--border: #332c20;
--hairline: #2a251b;
--accent: #c67a4e;
--accent-hover: #d68a5e;
--accent-fg: #17140f;
--accent-soft: rgba(198, 122, 78, 0.14);
--ok: #7a9c62;
--warn: #c69844;
--danger: #c25a4a;
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
html { font-size: 15px; }

body {
font-family: var(--font-sans);
font-size: 0.9375rem;
line-height: 1.55;
background: var(--bg);
color: var(--fg);
-webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4 {
font-family: var(--font-serif);
font-weight: 500;
letter-spacing: -0.005em;
margin: 0 0 var(--space-3);
color: var(--fg);
}
h1 { font-size: 1.85rem; line-height: 1.15; }
h2 { font-size: 1.35rem; line-height: 1.2; }
h3 { font-size: 1.1rem; }
h4 { font-size: 0.95rem; font-weight: 600; }

a { color: inherit; text-decoration: none; }
a:hover { color: var(--accent); }

.nowrap { white-space: nowrap; font-variant-numeric: tabular-nums; }
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.muted { color: var(--muted-fg); }

.layout {
display: grid;
grid-template-columns: 220px 1fr;
min-height: 100vh;
}

.sidebar {
background: var(--surface);
border-right: 1px solid var(--border);
display: flex;
flex-direction: column;
padding: var(--space-5) var(--space-4);
position: sticky;
top: 0;
height: 100vh;
width: 220px;
}

.sidenav {
display: flex;
flex-direction: column;
gap: 1px;
flex: 1;
overflow-y: auto;
margin: 0 calc(var(--space-2) * -1);
}

.navlink {
display: block;
padding: 7px var(--space-2);
border-radius: var(--radius-sm);
color: var(--muted-fg);
font-size: 0.86rem;
font-weight: 450;
letter-spacing: -0.005em;
transition: background .1s, color .1s;
}
.navlink:hover { background: var(--surface-2); color: var(--fg); }
.navlink.active { color: var(--accent); font-weight: 550; }

.sidebar-footer {
border-top: 1px solid var(--hairline);
padding-top: var(--space-4);
display: flex;
flex-direction: column;
gap: var(--space-3);
}

.user-chip {
display: flex;
align-items: center;
gap: var(--space-3);
padding: var(--space-1) var(--space-2);
margin: 0 calc(var(--space-2) * -1);
}

.footer-actions {
display: flex;
gap: var(--space-2);
padding: 0 var(--space-2);
margin: 0 calc(var(--space-2) * -1);
}

.icon-btn {
width: 30px;
height: 30px;
border-radius: var(--radius-sm);
background: transparent;
border: 1px solid var(--border);
color: var(--muted-fg);
font-size: 0.85rem;
cursor: pointer;
display: inline-flex;
align-items: center;
justify-content: center;
position: relative;
transition: background .1s, color .1s, border-color .1s;
}

.main {
padding: var(--space-6) var(--space-7);
max-width: none;
}

.topbar {
display: flex;
justify-content: flex-end;
align-items: center;
min-height: 40px;
margin-bottom: var(--space-5);
}

.page-head {
display: flex;
align-items: flex-end;
justify-content: space-between;
gap: var(--space-5);
margin-bottom: var(--space-6);
padding-bottom: var(--space-4);
border-bottom: 1px solid var(--hairline);
flex-wrap: wrap;
}

.eyebrow {
font-size: 0.7rem;
font-weight: 500;
letter-spacing: 0.14em;
text-transform: uppercase;
color: var(--muted-fg);
margin: 0 0 var(--space-2);
font-family: var(--font-mono);
}

.card {
background: var(--surface);
border: 1px solid var(--border);
border-radius: var(--radius);
padding: var(--space-5);
box-shadow: none;
margin-bottom: var(--space-4);
}

.card-head {
display: flex;
align-items: baseline;
justify-content: space-between;
margin-bottom: var(--space-3);
gap: var(--space-3);
flex-wrap: wrap;
}

.card-head h2 {
font-family: var(--font-mono);
font-size: 0.72rem;
font-weight: 500;
letter-spacing: 0.14em;
text-transform: uppercase;
color: var(--muted-fg);
margin: 0;
}

.btn {
display: inline-flex;
align-items: center;
justify-content: center;
gap: var(--space-2);
padding: 8px 14px;
border-radius: var(--radius-sm);
border: 1px solid var(--border);
background: var(--surface);
color: var(--fg);
font-family: var(--font-sans);
font-size: 0.86rem;
font-weight: 500;
letter-spacing: -0.005em;
cursor: pointer;
transition: background .1s, border-color .1s, color .1s;
text-decoration: none;
line-height: 1.3;
}
.btn:hover { background: var(--surface-2); }

.btn-primary {
background: var(--accent);
border-color: var(--accent);
color: var(--accent-fg);
}
.btn-primary:hover {
background: var(--accent-hover);
border-color: var(--accent-hover);
color: var(--accent-fg);
}

.btn-ghost { border-color: transparent; color: var(--muted-fg); }
.btn-ghost:hover { color: var(--fg); background: var(--surface-2); }

.btn-danger {
color: var(--danger);
border-color: var(--border);
background: transparent;
}
.btn-danger:hover {
background: var(--danger);
color: #fff;
border-color: var(--danger);
}

.btn-small { padding: 4px 9px; font-size: 0.78rem; }
.btn-block { width: 100%; }

.form-row {
display: flex;
flex-direction: column;
gap: var(--space-1);
margin-bottom: var(--space-4);
}

.form-row.two-up {
display: grid;
grid-template-columns: 1fr 1fr;
gap: var(--space-3);
}

.form-row label {
font-family: var(--font-mono);
font-size: 0.68rem;
font-weight: 500;
letter-spacing: 0.1em;
text-transform: uppercase;
color: var(--muted-fg);
}

.form-row input,
.form-row select,
.form-row textarea {
width: 100%;
padding: 8px 10px;
border: 1px solid var(--border);
border-radius: var(--radius-sm);
background: var(--surface);
color: var(--fg);
font-family: var(--font-sans);
font-size: 0.9rem;
transition: border-color .1s, box-shadow .1s;
}

.form-row input:focus,
.form-row select:focus,
.form-row textarea:focus {
outline: none;
border-color: var(--accent);
box-shadow: 0 0 0 3px var(--accent-soft);
}

fieldset.form-section {
border: none;
padding: 0;
margin: 0 0 var(--space-5);
}

.form-error,
.errorlist {
color: var(--danger);
font-size: 0.82rem;
list-style: none;
padding: 0;
margin: var(--space-1) 0 0;
}

.form-actions {
display: flex;
gap: var(--space-2);
margin-top: var(--space-4);
}

.checkbox-line {
display: flex;
align-items: center;
gap: var(--space-2);
font-family: var(--font-sans);
font-size: 0.9rem;
font-weight: 450;
letter-spacing: 0;
text-transform: none;
color: var(--fg);
}
.checkbox-line input[type="checkbox"] {
width: auto;
margin: 0;
}

.data-table,
.public-table {
width: 100%;
border-collapse: collapse;
font-size: 0.875rem;
}

.data-table th,
.data-table td,
.public-table th,
.public-table td {
padding: 9px 12px;
text-align: left;
border-bottom: 1px solid var(--hairline);
vertical-align: top;
}

.empty-state {
color: var(--muted-fg);
text-align: center;
padding: var(--space-5);
font-style: italic;
}

.stat-grid {
display: grid;
grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
gap: 0;
margin-bottom: var(--space-5);
border: 1px solid var(--border);
border-radius: var(--radius);
overflow: hidden;
background: var(--surface);
}

.stat-card {
padding: var(--space-4) var(--space-5);
border-right: 1px solid var(--hairline);
display: flex;
flex-direction: column;
gap: var(--space-1);
}
.stat-card:last-child { border-right: none; }

.stat-value {
font-family: var(--font-serif);
font-size: 1.7rem;
font-weight: 500;
line-height: 1;
letter-spacing: -0.015em;
}

.stat-label {
font-family: var(--font-mono);
font-size: 0.68rem;
font-weight: 500;
letter-spacing: 0.1em;
text-transform: uppercase;
color: var(--muted-fg);
}

.week-nav {
display: flex;
align-items: center;
gap: var(--space-2);
margin-bottom: var(--space-4);
}

.week-grid {
display: grid;
grid-template-columns: repeat(7, minmax(0, 1fr));
gap: 0;
border: 1px solid var(--border);
border-radius: var(--radius);
background: var(--surface);
overflow: hidden;
}

.week-col {
min-width: 0;
border-right: 1px solid var(--hairline);
display: flex;
flex-direction: column;
}
.week-col:last-child { border-right: none; }
.week-col.today { background: var(--accent-soft); }

.week-col-head {
padding: 10px 12px;
border-bottom: 1px solid var(--hairline);
}

.week-col-head strong {
display: block;
font-family: var(--font-mono);
font-size: 0.68rem;
letter-spacing: 0.12em;
text-transform: uppercase;
color: var(--muted-fg);
font-weight: 500;
}

.week-col-head small {
display: block;
color: var(--fg);
font-size: 0.86rem;
margin-top: 1px;
}

.week-col-body {
min-height: 130px;
padding: var(--space-2);
display: flex;
flex-direction: column;
gap: var(--space-1);
}

.event-chip {
display: block;
padding: 6px 8px;
border-radius: var(--radius-sm);
background: var(--surface-2);
color: inherit;
text-decoration: none;
font-size: 0.78rem;
border-left: 2px solid var(--muted-fg);
transition: background .1s;
}
.event-chip:hover { background: var(--accent-soft); color: var(--fg); }
.event-chip.service-chip { border-left-color: var(--accent); }
.event-chip strong { display: block; font-weight: 500; line-height: 1.25; }
.event-chip small {
color: var(--muted-fg);
display: block;
margin-top: 1px;
font-size: 0.7rem;
}

.empty-day {
color: var(--muted-fg);
font-size: 0.76rem;
padding: var(--space-2);
text-align: center;
font-style: italic;
}

.status-badge {
display: inline-block;
padding: 2px 7px;
border-radius: var(--radius-pill);
font-family: var(--font-mono);
font-size: 0.66rem;
font-weight: 500;
letter-spacing: 0.04em;
background: var(--surface-2);
color: var(--muted-fg);
}
.status-frozen,
.status-completed,
.status-approved {
background: rgba(90, 122, 68, 0.12);
color: var(--ok);
}
.status-in_progress,
.status-changed,
.status-pending {
background: rgba(168, 122, 42, 0.12);
color: var(--warn);
}
.status-skipped,
.status-rejected,
.status-cancelled {
background: rgba(158, 58, 46, 0.12);
color: var(--danger);
}

.freeze-banner {
padding: 10px 14px;
border-left: 2px solid var(--ok);
background: rgba(90, 122, 68, 0.06);
margin-bottom: var(--space-4);
font-size: 0.86rem;
color: var(--fg);
}

.filter-tabs {
display: flex;
gap: var(--space-3);
margin-bottom: var(--space-4);
border-bottom: 1px solid var(--border);
}
.filter-tabs a {
padding: 6px 0;
color: var(--muted-fg);
font-size: 0.86rem;
font-weight: 500;
border-bottom: 2px solid transparent;
margin-bottom: -1px;
transition: color .1s, border-color .1s;
}
.filter-tabs a:hover { color: var(--fg); }
.filter-tabs a.active { color: var(--accent); border-bottom-color: var(--accent); }

.notif-bell { position: relative; }
.notif-badge {
position: absolute;
top: -4px;
right: -4px;
min-width: 15px;
padding: 0 4px;
border-radius: var(--radius-pill);
background: var(--accent);
color: var(--accent-fg);
font-family: var(--font-mono);
font-size: 0.62rem;
font-weight: 500;
text-align: center;
line-height: 1.5;
}
.notif-dropdown {
position: absolute;
right: 0;
top: calc(100% + 6px);
z-index: 20;
width: 320px;
max-height: 420px;
overflow-y: auto;
padding: var(--space-2);
border: 1px solid var(--border);
border-radius: var(--radius);
background: var(--surface);
box-shadow: var(--shadow-lg);
}
.notif-item {
display: block;
padding: var(--space-3);
border-bottom: 1px solid var(--hairline);
color: inherit;
text-decoration: none;
border-radius: var(--radius-sm);
}
.notif-item:hover { background: var(--surface-2); }
.notif-item:last-child { border-bottom: 0; }
.notif-item strong { font-weight: 550; font-size: 0.86rem; display: block; }
.notif-item small {
display: block;
margin-top: 2px;
color: var(--muted-fg);
font-size: 0.76rem;
}

.toast-stack {
position: fixed;
right: var(--space-5);
bottom: var(--space-5);
display: flex;
flex-direction: column-reverse;
gap: var(--space-2);
z-index: 2000;
max-width: 340px;
pointer-events: none;
}
.toast {
pointer-events: auto;
padding: 10px 14px;
border-radius: var(--radius);
background: var(--fg);
color: var(--bg);
font-size: 0.86rem;
box-shadow: var(--shadow-lg);
opacity: 0;
transform: translateY(6px);
transition: opacity .16s ease, transform .16s ease;
}
.toast.show { opacity: 1; transform: translateY(0); }
.toast--success { background: var(--accent); color: var(--accent-fg); }
.toast--error { background: var(--danger); color: #fff; }
.toast--info { background: var(--fg); color: var(--bg); }

.inline-form {
display: flex;
gap: var(--space-2);
align-items: center;
flex-wrap: wrap;
margin: 0;
}

.row-actions-inline {
display: flex;
align-items: center;
gap: 6px;
white-space: nowrap;
flex-wrap: nowrap;
}
.row-actions-inline > .inline-form {
display: inline-flex;
margin: 0;
padding: 0;
}
.row-actions-inline .btn-small {
padding: 4px 10px;
font-size: 0.78rem;
line-height: 1.3;
}

.modal-backdrop {
position: fixed;
top: 0;
right: 0;
bottom: 0;
left: 0;
background: rgba(20, 15, 8, 0.5);
display: flex;
align-items: center;
justify-content: center;
padding: var(--space-4);
z-index: 1000;
}
.modal-backdrop[hidden] {
display: none !important;
}

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
box-shadow: 0 12px 40px rgba(40, 25, 10, 0.22);
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
letter-spacing: -0.005em;
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
.modal-body > p:first-child { margin-top: 0; }
.modal .form-row { margin-bottom: var(--space-4); }
.modal .form-actions {
display: flex;
gap: var(--space-2);
justify-content: flex-end;
margin-top: var(--space-5);
padding-top: var(--space-4);
border-top: 1px solid var(--hairline);
}

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
ENDOFCSS

echo "Step 1 complete."
wc -l static/css/harpr.css