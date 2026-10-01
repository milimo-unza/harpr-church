# Harpr Church build log

## Sprint 1 — April 16–30, 2026

Django scaffolding, authentication foundation, first church domain
entities. Kept the code small enough to explain in a viva.

## Sprint 2 — May 1–31, 2026

Early experiments with task CRUD, calendar concepts, time tracking. Settled
the warm paper visual language and the need for clear planned-vs-actual
times.

## Sprint 3 — June 1–30, 2026

Pivot to a church operations platform after supervisor feedback. The core
question became how a weekly programme moves from planning to a public
bulletin.

## Sprint 4 — July 1–31, 2026

Multi-tenancy, departments, memberships, service templates, service items,
audit logs, and the recalculation engine. Freeze/unfreeze workflow added so
a published bulletin stays stable while planning continues.

## Sprint 5 — August 1–31, 2026

Public schedules, ReportLab PDF bulletins, QR codes, notifications, and
aggregated operations reporting. The AI feature sends only summary numbers,
never names or individual member data.

## Sprint 6 — September 1–October 15, 2026

UI polish, department rosters, the requests workflow (announcements vs
schedule), modal-based interaction throughout, seed data, documentation,
and route tests for deployment.

## Scope cuts

- Pomodoro timers, removed — unrelated to the church workflow
- WeasyPrint, dropped in favour of ReportLab (fewer deployment deps)
- Browser push notifications — deferred in favour of in-app notifications

## What would be done differently

Define the public and staff URL map earlier and write route-level tests
before building templates. Use PostgreSQL from the start if multi-church
concurrent editing were ever intended.

## Future work

Recurring-event rules, password reset email, calendar export, mobile offline
support, PostgreSQL deployment, and richer department performance reporting.
