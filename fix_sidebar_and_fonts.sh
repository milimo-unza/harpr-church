#!/bin/bash

# Appends missing sidebar-brand rules, upscales the type, and removes

# JetBrains Mono site-wide (replaces with sans-serif, following Notion).

set -e
cd ~/harpr

cp static/css/harpr.css static/css/harpr.css.pre-font-fix

# 1. Bump base size slightly (15px -> 16px)

sed -i 's/^html { font-size: 15px; }/html { font-size: 16px; }/' static/css/harpr.css
sed -i 's/^  font-size: 0.9375rem;/  font-size: 0.95rem;/' static/css/harpr.css

# 2. Replace every JetBrains Mono reference with the sans stack

sed -i 's/--font-mono: .JetBrains Mono., ui-monospace, Menlo, monospace;/--font-mono: var(--font-sans);/' static/css/harpr.css

cat >> static/css/harpr.css << 'ENDOFCSS'

/* ============================================================
Sidebar brand — the missing rules
============================================================ */

.sidebar-brand {
display: flex;
align-items: center;
gap: 12px;
padding: 4px 4px 22px;
margin-bottom: 20px;
border-bottom: 1px solid var(--hairline);
text-decoration: none;
color: inherit;
}

.brand-mark {
width: 40px;
height: 40px;
flex: none;
border-radius: 10px;
background: var(--accent);
color: var(--accent-fg);
display: inline-flex;
align-items: center;
justify-content: center;
font-family: var(--font-serif);
font-size: 1.4rem;
font-weight: 600;
line-height: 1;
}

.brand-text {
display: flex;
flex-direction: column;
min-width: 0;
}

.brand-name {
font-family: var(--font-serif);
font-size: 1.15rem;
font-weight: 600;
line-height: 1.1;
color: var(--fg);
}

.brand-tagline {
font-family: var(--font-sans);
font-size: 0.72rem;
color: var(--muted-fg);
margin-top: 3px;
line-height: 1.2;
letter-spacing: 0.01em;
overflow: hidden;
text-overflow: ellipsis;
white-space: nowrap;
max-width: 150px;
}

/* Sidebar user chip */
.user-avatar {
width: 34px;
height: 34px;
flex: none;
border-radius: 8px;
background: var(--surface-2);
border: 1px solid var(--border);
color: var(--fg);
display: inline-flex;
align-items: center;
justify-content: center;
font-family: var(--font-sans);
font-size: 0.75rem;
font-weight: 600;
letter-spacing: 0.02em;
}

.user-meta {
display: flex;
flex-direction: column;
min-width: 0;
}

.user-name {
font-family: var(--font-sans);
font-size: 0.84rem;
font-weight: 550;
line-height: 1.15;
color: var(--fg);
overflow: hidden;
text-overflow: ellipsis;
white-space: nowrap;
max-width: 130px;
}

.user-role {
font-family: var(--font-sans);
font-size: 0.7rem;
color: var(--muted-fg);
margin-top: 2px;
line-height: 1.2;
}

/* ============================================================
Notion-style typography — no monospace in the UI
============================================================ */

/* Eyebrows: small sans-serif, letter-spaced, muted */
.eyebrow,
.card-head h2,
.section-label {
font-family: var(--font-sans);
font-size: 0.72rem;
font-weight: 600;
letter-spacing: 0.06em;
text-transform: uppercase;
color: var(--muted-fg);
}

.card-head h2 { font-size: 0.78rem; }

/* Form labels: sans-serif, sentence-case-ish, medium weight */
.form-row label,
.auth-field label {
font-family: var(--font-sans);
font-size: 0.82rem;
font-weight: 550;
letter-spacing: 0;
text-transform: none;
color: var(--fg);
}

/* Stat labels */
.stat-label {
font-family: var(--font-sans);
font-size: 0.76rem;
font-weight: 500;
letter-spacing: 0.02em;
text-transform: none;
color: var(--muted-fg);
}

/* Status badges: soft sans, not mono */
.status-badge {
font-family: var(--font-sans);
font-size: 0.72rem;
font-weight: 550;
letter-spacing: 0.01em;
}

/* Notification items */
.notif-item strong {
font-family: var(--font-sans);
font-weight: 600;
}

/* Table cells that were styled mono */
.mono,
td.mono,
.data-table td.mono,
.public-table td.mono {
font-family: var(--font-sans);
font-variant-numeric: tabular-nums;
letter-spacing: 0;
}

/* Tabular numbers still respect alignment */
.nowrap {
font-family: var(--font-sans);
font-variant-numeric: tabular-nums;
}

/* Stat values: keep serif, they look right */
.stat-value {
font-family: var(--font-serif);
}

/* Form-section legends */
.form-section legend {
font-family: var(--font-sans);
font-size: 0.74rem;
font-weight: 600;
letter-spacing: 0.08em;
text-transform: uppercase;
color: var(--muted-fg);
}

/* Week column heads */
.week-col-head strong {
font-family: var(--font-sans);
font-size: 0.72rem;
font-weight: 600;
letter-spacing: 0.08em;
text-transform: uppercase;
color: var(--muted-fg);
}

/* Filter tabs */
.filter-tabs a {
font-family: var(--font-sans);
font-weight: 550;
}
ENDOFCSS

echo "Font and sidebar fix complete."
wc -l static/css/harpr.css
grep -c "JetBrains Mono" static/css/harpr.css