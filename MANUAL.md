# Harpr Church manual

## Part 1 — Programme Coordinator

Sign in at `/accounts/login/`. The sidebar has eight sections.

**Dashboard** shows the Sunday-first week, service and event counts, pending
requests, and a shortcut to create a new event or service.

**Services** lists every service, filterable by upcoming, past, or all. Click
a service to manage its items, assignments, times, and bulletin state.

**Requests** shows inbound requests from department heads and the public,
grouped by pending, approved, and rejected. Click any row to open the review
modal. Approving an announcement request requires your own wording, which
becomes the public announcement. Approving a schedule request requires the
date and time, which becomes the church event.

**Departments** manages the church's teams. **Members** handles who has
access and what role they hold.

**Announcements** manages the public announcements shown on the schedule
and included in the bulletin PDF.

**Report** shows aggregated operations stats and optional AI commentary.

**Settings** manages the church profile, footer contacts, and worship day.

## Part 2 — Department Head

Sign in as one of the department head accounts. The sidebar has three items.

**My department** shows the church week grid with your department's items
highlighted, a pending assignments table, upcoming items, and a recent
changes panel scoped to your items. Click any row to open the assignment
modal. Pick saved team names by clicking checkboxes, or type a new name.
Already-assigned names are greyed out.

**My requests** lists your submissions. Click a row to view, edit, or
withdraw a pending request. Approved and rejected requests show the
coordinator's response and a green dot next to the title.

**My team** is the department roster. Names added here appear as checkboxes
in the assignment modal. Edit phone numbers inline. Remove people no longer
in the department.

## Part 3 — Public

Open `/c/<church-slug>/` to see today's service or the next upcoming one,
the announcements currently running, and the church's contact footer.

Download the bulletin PDF with the button at the top of the service card.

Submit an announcement request at `/c/<slug>/request/`. The form validates
your name, a phone or email, a title, what you'd like announced, and a date
range. The coordinator reviews it and writes the final wording before it
appears publicly.

## Tips and troubleshooting

- `python manage.py migrate` after pulling model changes
- `python manage.py seed_demo` rebuilds the demonstration church
- If the Report page says AI is unavailable, set `GROQ_API_KEY` in `.env`
- A frozen service must be unfrozen with a written reason before its plan
  changes
- `python manage.py check` and `python manage.py test church` before
  reporting a deployment issue
