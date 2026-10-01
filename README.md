# Harpr Church

A Django 6 platform for planning, publishing, and analysing weekly church
programmes. Built as a final-year BSc Computer Science project by Milimo
Kasamba Mukkuli (2021515567) at the University of Zambia under Prof. J. Phiri.

## What it does

Three roles interact with one church.

**Programme Coordinator** schedules services and church events, manages
departments and members, reviews requests from department heads and the
public, publishes bulletins, and reviews an operations report on schedule
drift.

**Department Head** sees the church-wide week at a glance, manages their own
department's assignments against a saved team roster, and submits requests
for announcements or for additions to the calendar.

**Public visitors** view the schedule and announcements, download a bulletin
PDF, and submit announcement requests without an account.

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

## Limitations and future work

SQLite for a student demonstration. No recurring-event rules, no email
backend (console backend only), no browser push notifications. Future work
could add PostgreSQL, calendar export, richer analytics, and an actual
deployment pipeline.
