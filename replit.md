# Harpr Church on Replit

## Run the project

    python manage.py runserver 0.0.0.0:5000

Django 6, SQLite, server-rendered templates, vanilla JavaScript.
Dependencies are in `requirements.txt`.

For a fresh database:

    python manage.py migrate
    python manage.py seed_demo

Open `/accounts/login/`. Demo users share the password `harpr2026`.
Coordinator: `coordinator`. Department heads: `music_head`, `pastors_head`,
`ushering_head`, `media_head`.

The public demo page is `/c/grace-covenant/`.

## Optional configuration

Set `GROQ_API_KEY` to enable the AI commentary on the Report page. The rest
of the application works without it. `SESSION_SECRET` is accepted as the
Django secret key.
