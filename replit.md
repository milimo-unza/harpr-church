# Harpr Church on Replit

## Run the project

The configured workflow is **Start application**:

```bash
python manage.py runserver 0.0.0.0:5000
```

The app uses Django 6, SQLite, server-rendered templates, and vanilla
JavaScript. Dependencies are listed in `requirements.txt`.

For a fresh database:

```bash
python manage.py migrate
python manage.py seed_demo
```

Open `/accounts/login/` to sign in. The demo users use the password
`harpr2026`; the coordinator is `coordinator`, and department-head users
include `music_head`, `pastors_head`, `ushering_head`, and `media_head`.

The public demo page is `/c/grace-covenant/`.

## Optional configuration

Set `GROQ_API_KEY` to enable the optional AI insights page. The rest of the
application works without it. `SESSION_SECRET` is accepted as the Django
secret key in Replit environments.