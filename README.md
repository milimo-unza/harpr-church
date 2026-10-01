# Harpr Church

A Django 6 platform for planning, publishing, and analysing weekly church
programmes. Built as a final-year BSc Computer Science project by Milimo
Kasamba Mukkuli (2021515567) at the University of Zambia under Prof. J. Phiri.

## What it does

I built this as my final year project. It is a scheduling tool for a church
that wants its weekly programme online, and wants the staff to be able to
plan it without a spreadsheet.

Three types of user:

- **Programme Coordinator** plans services and events, manages departments
  and members, reviews requests, and publishes bulletins. Can see an
  operations report on how services actually run compared to plan.
- **Department Head** sees the week for the whole church, manages the people
  in their own department, and asks the coordinator for changes.
- **Public visitors** see the schedule and announcements, download the
  bulletin PDF, and send in announcements without needing an account.

## Features

- Multi-tenant Church, Membership, Department, Service, ChurchEvent data
- Sunday-first weekly programme grid for coordinators and department heads
- Recurring service templates and generated service items
- Time recalculation with locked and completed item protection
- Versioned bulletin freeze/unfreeze workflow with audit logs
- Department rosters with quick-pick assignment
- Requests with two types: announcements and schedule additions
- Approving a request auto-creates an Announcement or a ChurchEvent
- Public schedule, PDF bulletin, QR code, and public request form
- In-app notifications and optional Groq-powered operations commentary
- Operations report with aggregated delay, overrun, and completion stats

## Tech stack

Python 3.12, Django 6, SQLite, Django templates, vanilla JavaScript,
WhiteNoise, ReportLab, qrcode, OpenAI-compatible Groq client, Pillow.
No React, no build step, no separate API server.

## Running locally

    python -m pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed_demo
    python manage.py runserver 0.0.0.0:5000

Open http://127.0.0.1:5000/accounts/login/

### Demo credentials

- Coordinator: `coordinator` / `harpr2026`
- Department heads: `music_head`, `pastors_head`, `ushering_head`, or
  `media_head` / `harpr2026`
- Public page: `/c/grace-covenant/`

### Optional configuration

Copy `.env.example` to `.env` and fill in `GROQ_API_KEY` to enable the
AI commentary on the Report page. Everything else works without it.

## Project layout

    harpr_church/       Django settings and project URLs
    church/models.py    Domain models
    church/views/       Coordinator, department, public views
    church/services/    Recalculation, freeze, PDF, QR, notifications
    church/templates/   Server-rendered pages
    static/             CSS and notification JS

## Limitations

- SQLite only. Fine for one church, not for many at once.
- No recurring event rules yet, you have to add each one.
- Emails print to the console unless you set up SMTP.
- No browser push, only in-app notifications.

If I had more time I would add event recurrence, proper deployment, and a
month view on the dashboard.
