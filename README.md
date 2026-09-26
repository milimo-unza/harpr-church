# Harpr Church

Harpr Church is a Django 6 platform for planning, publishing, and analysing
weekly church programmes. It was built as a final-year BSc Computer Science
project by **Milimo Kasamba Mukkuli (2021515567)** at the University of
Zambia under **Prof. J. Phiri**.

## What it does

Programme Coordinators can schedule services and church events, assign
departments and people, freeze a bulletin, respond to requests, and review
operational trends. Department Heads see only the items assigned to their
department and can fill in assignments or submit requests. The public can view
an active church's programme, download a bulletin PDF, and save the church
locally in the browser.

## Features

- Multi-tenant Church, Membership, Department, Service, and ChurchEvent data.
- Weekly Monday–Sunday coordinator dashboard.
- Recurring service templates and generated service items.
- Time recalculation with locked and completed item protection.
- Versioned bulletin freeze/unfreeze workflow with audit logs.
- Department-head assignment and request workflows.
- Public schedule, PDF bulletin, QR code, and public request form.
- In-app notifications and optional Groq-powered aggregated insights.
- Harpr's warm paper visual language adapted for church operations.

## Tech stack

Python 3.12, Django 6, SQLite, Django templates, vanilla JavaScript,
WhiteNoise, ReportLab, qrcode, OpenAI-compatible Groq client, and Pillow.
There is no React, TypeScript, Node build step, or separate API server.

## Running locally

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 0.0.0.0:5000
```

Open `http://127.0.0.1:5000/accounts/login/`.

Demo credentials:

- Coordinator: `coordinator` / `harpr2026`
- Department heads: `music_head`, `pastors_head`, `ushering_head`, or
  `media_head` / `harpr2026`
- Public page: `/c/grace-covenant/`

Copy `.env.example` to `.env` or set environment variables directly. A Groq
API key is optional; the AI page reports that analysis is unavailable when no
key is configured.

## Project layout

```text
harpr_church/       Django settings and project URLs
church/models.py    Church domain models
church/views/       Coordinator, department, public, and notification views
church/services/    Recalculation, freeze, PDF, QR, and notification services
church/templates/  Server-rendered pages
static/             Existing cosmos.css plus church-only additions
```

## Limitations and future work

The project uses SQLite for a simple student demonstration and does not yet
include recurring-service generation, password reset email, browser push
notifications, or an external production database. Future work could add
PostgreSQL, stronger invitation flows, calendar exports, and richer analytics.