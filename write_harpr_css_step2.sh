#!/bin/bash

# Step 2 of 2 — appends the remaining rules to static/css/harpr.css

# Run from ~/harpr after step 1 has completed.

set -e
cd ~/harpr

cat >> static/css/harpr.css << 'ENDOFCSS'

/* ====================== public pages ====================== */

.public-body { background: var(--bg); }

.public-shell {
padding: var(--space-6);
max-width: 900px;
margin: 0 auto;
}

.public-head {
display: flex;
justify-content: space-between;
align-items: center;
margin-bottom: var(--space-4);
}

.public-card {
background: var(--surface);
border: 1px solid var(--border);
padding: var(--space-4);
border-radius: var(--radius);
margin-bottom: var(--space-4);
}

.public-links { list-style: none; padding: 0; margin: 0; }

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

.saved-list {
list-style: none;
padding: 0;
margin: 0;
display: flex;
gap: var(--space-2);
flex-wrap: wrap;
}

/* ====================== auth pages ====================== */

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
.auth-topbar-brand { display: flex; flex-direction: column; }
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
content: "!";
font-size: 1rem;
font-weight: 700;
line-height: 1;
flex: none;
width: 18px;
height: 18px;
border-radius: 50%;
border: 1.5px solid var(--danger);
display: inline-flex;
align-items: center;
justify-content: center;
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
.auth-btn-outline:hover { background: var(--surface-2); color: var(--fg); }

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

/* ====================== django form fallbacks ====================== */

form p { margin: 0 0 16px; }
form p label {
display: block;
font-family: var(--font-mono);
font-size: 0.68rem;
font-weight: 500;
letter-spacing: 0.1em;
text-transform: uppercase;
color: var(--muted-fg);
margin-bottom: 6px;
}
form p input,
form p select,
form p textarea {
width: 100%;
padding: 8px 10px;
border: 1px solid var(--border);
border-radius: var(--radius-sm);
background: var(--surface);
color: var(--fg);
font-family: var(--font-sans);
font-size: 0.9rem;
}
form p input:focus,
form p select:focus,
form p textarea:focus {
outline: none;
border-color: var(--accent);
box-shadow: 0 0 0 3px var(--accent-soft);
}
form p .helptext,
form p ul {
font-size: 0.74rem;
color: var(--muted-fg);
margin-top: 5px;
padding-left: 18px;
}

.narrow-page { max-width: 760px; margin: 0 auto; }
.form-card p { margin: 0 0 1rem; }
.form-card label { display: block; margin-bottom: 0.25rem; font-weight: 600; }
.form-input {
width: 100%;
padding: 0.55rem 0.65rem;
border: 1px solid var(--border);
border-radius: var(--radius-sm);
background: var(--surface);
color: var(--fg);
}
.page-actions { margin-top: 1rem; }
.qr-display { margin-top: 1rem; }
.qr-display img { width: 220px; height: 220px; display: block; margin: 1rem 0; }
.insight-card { margin-bottom: 1rem; font-size: 1.05rem; }

/* ====================== mobile ====================== */

@media (max-width: 1024px) {
.week-grid {
overflow-x: auto;
grid-template-columns: repeat(7, minmax(150px, 1fr));
}
.layout { grid-template-columns: 200px 1fr; }
}

@media (max-width: 768px) {
.layout { display: block; grid-template-columns: 1fr; }
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
.navlink { padding: 6px 12px; font-size: 0.82rem; white-space: nowrap; }
.sidebar-footer {
flex-direction: row;
justify-content: space-between;
align-items: center;
margin-top: var(--space-3);
}
.main { padding: var(--space-4); }
.page-head {
flex-direction: column;
align-items: stretch;
gap: var(--space-3);
padding-bottom: var(--space-3);
}
.page-head h1 { font-size: 1.4rem; }
.page-head .button-row { display: flex; gap: var(--space-2); flex-wrap: wrap; }
.page-head .button-row .btn { flex: 1 1 auto; }
.week-grid {
display: flex;
overflow-x: auto;
scroll-snap-type: x mandatory;
-webkit-overflow-scrolling: touch;
border-radius: var(--radius);
}
.week-col { flex: 0 0 200px; scroll-snap-align: start; }
.stat-grid { grid-template-columns: 1fr 1fr; }
.stat-card { padding: var(--space-3); }
.stat-value { font-size: 1.4rem; }
}

@media (max-width: 640px) {
.table-wrap {
overflow-x: auto;
-webkit-overflow-scrolling: touch;
margin: 0 calc(var(--space-3) * -1);
padding: 0 var(--space-3);
}
.data-table, .public-table { font-size: 0.78rem; min-width: 540px; }
.data-table th, .data-table td,
.public-table th, .public-table td {
padding: 6px 8px;
white-space: nowrap;
}
.data-table th, .public-table th { font-size: 0.66rem; }
.form-row.two-up { grid-template-columns: 1fr; gap: var(--space-2); }
.form-row input, .form-row select, .form-row textarea {
font-size: 16px;
padding: 10px 12px;
}
.row-actions-inline { flex-wrap: wrap; gap: 4px; }
.row-actions-inline .btn-small { padding: 4px 8px; font-size: 0.72rem; }
.modal-backdrop { align-items: flex-end; padding: 0; }
.modal {
max-width: none;
margin: 0;
border-radius: var(--radius) var(--radius) 0 0;
align-self: flex-end;
max-height: 92vh;
}
.modal-head { padding: var(--space-3) var(--space-4); }
.modal-body { padding: var(--space-4); }
.modal .form-actions {
flex-direction: column-reverse;
gap: var(--space-2);
}
.modal .form-actions .btn { width: 100%; padding: 12px; }
.btn { padding: 10px 16px; font-size: 0.86rem; }
.btn-small { padding: 6px 10px; font-size: 0.78rem; }
.public-shell { padding: var(--space-4) var(--space-3) var(--space-6); }
.public-head {
flex-direction: column;
align-items: stretch;
gap: var(--space-3);
}
.public-head h1 { font-size: 1.5rem; }
.public-card { padding: var(--space-4) var(--space-3); }
.public-table { font-size: 0.8rem; }
.public-links { text-align: left; }
.auth-page { padding: var(--space-3); }
.auth-form-card, .auth-form-card--wide {
max-width: none;
padding: var(--space-5) var(--space-4);
}
.auth-form-header h1 { font-size: 1.4rem; }
.auth-topbar {
flex-direction: column;
align-items: flex-start;
gap: var(--space-2);
}
.auth-topbar-actions { width: 100%; justify-content: space-between; }
.public-footer .footer-contacts { flex-direction: column; gap: var(--space-2); }
.notif-dropdown {
position: fixed;
left: var(--space-3);
right: var(--space-3);
top: 60px;
width: auto;
max-width: none;
}
.section-label { font-size: 0.68rem; }
}

@media (max-width: 480px) {
.row-actions-inline { flex-wrap: wrap; white-space: normal; }
}

@media (max-width: 400px) {
.stat-grid { grid-template-columns: 1fr; }
.page-head h1 { font-size: 1.25rem; }
.btn { font-size: 0.8rem; padding: 9px 14px; }
}
ENDOFCSS

echo "Step 2 complete."
wc -l static/css/harpr.css
grep -c "@media" static/css/harpr.css
