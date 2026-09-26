# Harpr Church build log

## Sprint 1 — April 16–30, 2026

The project started as a Django application with the basic configuration,
authentication foundation, and the first church domain entities. The aim was
to keep the code small enough to explain during a viva.

## Sprint 2 — May 1–31, 2026

Early experiments focused on task CRUD, calendar concepts, and time tracking.
Those ideas helped establish the warm paper interface and the need for clear
planned-versus-actual times.

## Sprint 3 — June 1–30, 2026

After supervisor feedback, the generic planner was pivoted into a church
operations platform. The central question became how a weekly programme moves
from planning to a public bulletin.

## Sprint 4 — July 1–31, 2026

Multi-tenancy, departments, memberships, service templates, service items,
audit logs, and the recalculation engine were built. Freeze/unfreeze versions
were added so a published bulletin can remain stable while later planning
continues.

## Sprint 5 — August 1–31, 2026

Public schedules, ReportLab PDF bulletins, QR codes, notifications, and
aggregated AI insights were added. The AI feature deliberately sends only
summary numbers, not names or individual member data.

## Sprint 6 — September 1–October 15, 2026

The final sprint focuses on the Harpr Church templates, responsive styling,
seed data, documentation, route tests, and deployment preparation.

## Scope cuts

- Pomodoro timers were removed because they did not help the church
  programme workflow.
- WeasyPrint was not used because ReportLab has fewer deployment dependencies.
- Browser push notifications were deferred because they require a service
  worker and a push server; in-app notifications cover the core need.

## What I would do differently

I would define the public and staff URL map earlier and add route-level tests
before building the templates. I would also use PostgreSQL earlier if the
project were intended for multiple churches with concurrent editing.

## Future work

Recurring event rules, password reset email, calendar export, mobile offline
support, PostgreSQL deployment, and richer department performance reporting
would be useful next steps.