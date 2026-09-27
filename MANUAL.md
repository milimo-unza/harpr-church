# Harpr Church manual

## Part 1 — Programme Coordinator

1. Sign in at `/accounts/login/`.
2. Use Dashboard to see the Monday–Sunday programme.
3. Create a service from Services → New service. Select a service template to
   create its items automatically.
4. Open a service to add items, people, recalculated times, or a bulletin
   freeze.
5. Use Departments and Members to keep access aligned with church teams.
6. Review Requests, Announcements, AI insights, and Settings from the sidebar.

Freezing a service creates a numbered bulletin snapshot. To make a change,
unfreeze it with a written reason, make the change, and freeze it again.

## Part 2 — Department Head

The Department view shows upcoming items assigned to your department. Open an
item to add the person and role responsible for it. Submit programme changes
through My requests so the Coordinator can approve or reject them.

Department access is scoped to the active membership and department; it does
not expose another church's schedule.

## Part 3 — Public

Open `/c/<church-slug>/` to see today's service or the next upcoming service.
The page includes announcements, item times, departments, assignments, and a
PDF link. Use Save this church to store the slug in browser local storage.
Public visitors can use the request link without signing in.

## Tips and troubleshooting

- Run `python manage.py migrate` after pulling model changes.
- Run `python manage.py seed_demo` to restore the demonstration church.
- If AI insights say they are unavailable, check `GROQ_API_KEY`; the rest of
  the application does not depend on AI.
- A frozen service must be unfrozen with a reason before its plan changes.
- Use `python manage.py check` and `python manage.py test church` before
  reporting a deployment issue.