#!/bin/bash

# Round 4b, script 2a of 3.

# Step 1 of 2: writes the new seed_demo.py and a standalone patch script.

# Does NOT run the patch yet — that's the next step.

# Run from ~/harpr.

set -e
cd ~/harpr

echo "=== Backing up files ==="
mkdir -p .r4b_backup
cp church/views/admin_views.py .r4b_backup/admin_views.py.bak 2>/dev/null || true
cp church/management/commands/seed_demo.py .r4b_backup/seed_demo.py.bak 2>/dev/null || true
echo "Backups saved to .r4b_backup/"

echo ""
echo "=== Writing seed_demo.py ==="
cat > church/management/commands/seed_demo.py << 'ENDSEED'
from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from church.models import (
Announcement,
Assignment,
Church,
ChurchEvent,
Department,
Membership,
Service,
ServiceItem,
ServiceItemTemplate,
ServiceLog,
ServiceTemplate,
)

User = get_user_model()

class Command(BaseCommand):
help = "Rebuild the Harpr Church demonstration data."

def handle(self, *args, **options):
today = timezone.localdate()

church, _ = Church.objects.update_or_create(
slug="grace-covenant",
defaults={
"name": "Grace Covenant Church",
"timezone": "Africa/Lusaka",
"address": "Lusaka, Zambia",
"contact_phone": "+260 211 123 456",
"contact_email": "office@gracecovenant.org.zm",
"contact_whatsapp": "260971234567",
"footer_verse": "The Lord bless you and keep you. - Numbers 6:24",
"is_active": True,
},
)

departments = {}
for slug, name, color in [
("pastors", "Pastors", "#a85430"),
("music", "Music", "#4a7d57"),
("ushering", "Ushering", "#5a7ba0"),
("media", "Media", "#7865a0"),
("children", "Children", "#b58a30"),
("prayer", "Prayer", "#4a7a7c"),
]:
departments[slug], _ = Department.objects.update_or_create(
church=church, slug=slug,
defaults={"name": name, "color": color},
)

coordinator = self._user(
"coordinator", "coordinator@example.com", "Programme", "Coordinator"
)
Membership.objects.update_or_create(
user=coordinator, church=church,
defaults={"role": "admin", "department": None, "is_active": True},
)

heads = {
"music_head": ("music", "Music"),
"pastors_head": ("pastors", "Pastors"),
"ushering_head": ("ushering", "Ushering"),
"media_head": ("media", "Media"),
}
for username, (dept_slug, title) in heads.items():
user = self._user(username, f"{username}@example.com", title, "Head")
Membership.objects.update_or_create(
user=user, church=church,
defaults={
"role": "dept_head",
"department": departments[dept_slug],
"is_active": True,
},
)

template, _ = ServiceTemplate.objects.update_or_create(
church=church, name="Sunday Worship Service",
defaults={
"day_of_week": 6,
"default_start_time": time(8, 0),
"default_duration_minutes": 120,
"is_active": True,
},
)
item_specs = [
("Pre-Service Music", 10, "music"),
("Call to Worship", 5, "pastors"),
("Opening Prayer", 10, "prayer"),
("Worship Songs", 25, "music"),
("Scripture Reading", 5, "pastors"),
("Sermon", 45, "pastors"),
("Response Song", 10, "music"),
("Announcements", 10, "pastors"),
("Offering", 10, "ushering"),
("Benediction", 5, "pastors"),
]
for order, (title, duration, dept_slug) in enumerate(item_specs):
ServiceItemTemplate.objects.update_or_create(
template=template, order=order,
defaults={
"title": title,
"default_duration_minutes": duration,
"responsible_department": departments[dept_slug],
},
)

anchor = date(2026, 7, 5)
end = date(2026, 11, 29)
service_dates = []
cursor = anchor
while cursor <= end:
service_dates.append(cursor)
cursor += timedelta(days=7)

Service.objects.filter(church=church).delete()

names = {
"Sermon": ["Pastor Phiri", "Pastor Banda", "Pastor Mulenga"],
"Worship Songs": ["Ruth Mwansa", "Mwaka Zulu", "Chanda Tembo"],
"Offering": ["Moses Lungu", "Esther Chileshe", "Andrew Sakala"],
"Scripture Reading": ["Grace Mumba", "Brian Kunda", "Naomi Sampa"],
}

for idx, service_date in enumerate(service_dates):
is_past = service_date < today
service, _ = Service.objects.update_or_create(
church=church, date=service_date, name="Sunday Worship Service",
defaults={
"template": template,
"status": "completed" if is_past else "draft",
},
)
start = timezone.make_aware(datetime.combine(service_date, time(8, 0)))
for order, (title, duration, dept_slug) in enumerate(item_specs):
actual_start = start if is_past else None
actual_duration = duration if is_past else None
item, _ = ServiceItem.objects.update_or_create(
service=service, order=order,
defaults={
"title": title,
"planned_start": start,
"planned_duration_minutes": duration,
"actual_start": actual_start,
"actual_duration_minutes": actual_duration,
"status": "completed" if is_past else "planned",
"responsible_department": departments[dept_slug],
},
)
if title in names:
Assignment.objects.update_or_create(
service_item=item,
person_name=names[title][idx % len(names[title])],
role=title,
defaults={"church": church},
)
start += timedelta(minutes=duration)

ChurchEvent.objects.filter(church=church).delete()
event_templates = [
("Choir Practice", "rehearsal", 2, time(18, 0), time(19, 30), "music"),
("Bible Study", "study", 4, time(18, 30), time(20, 0), "pastors"),
("Youth Meeting", "meeting", 5, time(14, 0), time(16, 0), "children"),
("Prayer Meeting", "meeting", 5, time(9, 0), time(11, 0), "prayer"),
("Media Team Rehearsal", "rehearsal", 1, time(17, 0), time(18, 0), "media"),
("Chapel Practice", "rehearsal", 3, time(16, 0), time(17, 30), "music"),
("Church Cleaning", "meeting", 6, time(7, 0), time(8, 0), "ushering"),
]
for week_offset in range(0, 22, 1):
week_start = anchor + timedelta(weeks=week_offset)
if week_start > end:
break
for title, event_type, day_offset, start_time, end_time, dept_slug in event_templates:
ChurchEvent.objects.create(
church=church, title=title, event_type=event_type,
date=week_start + timedelta(days=day_offset),
start_time=start_time, end_time=end_time,
location="Main church campus",
responsible_department=departments[dept_slug],
)

Announcement.objects.filter(church=church).delete()
announcements = [
("Mid-week prayer meeting moves to Wednesday at 18:00. All are welcome.",
today - timedelta(days=60), today - timedelta(days=30)),
("The choir is recruiting new members. Speak to the music department.",
today - timedelta(days=45), today - timedelta(days=15)),
("Monthly outreach to Matero is this Saturday at 09:00. Meet at the car park.",
today - timedelta(days=7), today + timedelta(days=7)),
("Harvest thanksgiving service is on the last Sunday of October.",
today - timedelta(days=2), today + timedelta(days=20)),
("Youth camp registration closes at the end of the month.",
today + timedelta(days=5), today + timedelta(days=40)),
("New believers' class begins next month. Sign up with the pastors' department.",
today + timedelta(days=14), today + timedelta(days=60)),
]
for body, start_date, end_date in announcements:
Announcement.objects.create(
church=church, body=body,
start_date=start_date, end_date=end_date,
is_paused=False, show_on_public=True,
)

ServiceLog.objects.filter(church=church).delete()
recent_service = Service.objects.filter(
church=church, date__lt=today
).order_by("-date").first()
if recent_service:
ServiceLog.objects.create(
church=church, user=coordinator, service=recent_service,
action="frozen", details="Bulletin frozen for Sunday.",
)
ServiceLog.objects.create(
church=church, user=coordinator, service=recent_service,
action="item_completed", details="Service marked complete.",
)

self.stdout.write(self.style.SUCCESS("Harpr demo data rebuilt."))
self.stdout.write("Coordinator: coordinator / harpr2026")
self.stdout.write("Public URL: /c/grace-covenant/")

@staticmethod
def _user(username, email, first_name, last_name):
user, _ = User.objects.get_or_create(
username=username,
defaults={"email": email, "first_name": first_name, "last_name": last_name},
)
user.email = email
user.first_name = first_name
user.last_name = last_name
user.set_password("harpr2026")
user.save()
return user
ENDSEED
echo "seed_demo.py written. Lines: $(wc -l < church/management/commands/seed_demo.py)"

echo ""
echo "=== Writing patch_views.py ==="
cat > patch_views.py << 'ENDPATCH'
"""Standalone patch script for admin_views.py.
Replaces admin_dashboard with the Sunday-first version and adds
two member guards. Run once from ~/harpr."""

from pathlib import Path

path = Path("church/views/admin_views.py")
text = path.read_text()

# --- Fix 1: replace admin_dashboard ---

start_marker = "@admin_required\ndef admin_dashboard(request):"
end_marker = "\n\n@admin_required\ndef service_list(request):"

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx == -1 or end_idx == -1:
raise SystemExit("Could not locate admin_dashboard block. Aborting.")

new_dashboard = """@admin_required
def admin_dashboard(request):
from datetime import date, timedelta

today = timezone.localdate()
week_param = request.GET.get("week")

if week_param:
try:
ref = date.fromisoformat(week_param)
except (ValueError, TypeError):
ref = today
else:
ref = today

# Sunday-first week: Sunday.weekday() == 6, so shift forward by 1

days_since_sunday = (ref.weekday() + 1) % 7
week_start = ref - timedelta(days=days_since_sunday)
week_end = week_start + timedelta(days=6)

prev_week = week_start - timedelta(days=7)
next_week = week_start + timedelta(days=7)

services = request.church.services.filter(
date__range=(week_start, week_end)
).prefetch_related("items")
events = request.church.events.filter(
date__range=(week_start, week_end)
).select_related("responsible_department")

days = []
for day_offset in range(7):
day = week_start + timedelta(days=day_offset)
days.append({
"date": day,
"services": [s for s in services if s.date == day],
"events": [e for e in events if e.date == day],
})

return render(request, "church/dashboard.html", {
"church": request.church,
"today": today,
"week_start": week_start,
"week_end": week_end,
"prev_week": prev_week,
"next_week": next_week,
"days": days,
"service_count": request.church.services.filter(
date__year=today.year, date__month=today.month
).count(),
"pending_request_count": request.church.requests.filter(
status="pending"
).count(),
"recent_activity": request.church.logs.select_related(
"user", "service", "service_item"
)[:10],
"service_templates": request.church.service_templates.filter(is_active=True),
"departments": request.church.departments.all(),
})"""

text = text[:start_idx] + new_dashboard + text[end_idx:]

# --- Fix 2: Guard 1 ---

old_guard_1 = (
"def member_deactivate(request, pk):\n"
"    membership = get_object_or_404(request.church.memberships, pk=pk)\n"
"    membership.is_active = False"
)
new_guard_1 = (
"def member_deactivate(request, pk):\n"
"    membership = get_object_or_404(request.church.memberships, pk=pk)\n"
"    if membership.user == request.user:\n"
"        messages.error(request, "You cannot deactivate your own account.")\n"
"        return redirect("member_list")\n"
"    membership.is_active = False"
)

if old_guard_1 not in text:
raise SystemExit("Guard 1 target not found. Aborting.")
text = text.replace(old_guard_1, new_guard_1, 1)

# --- Fix 3: Guard 2 ---

old_guard_2 = (
"    if request.method == "POST" and form.is_valid():\n"
"        data = form.cleaned_data\n"
"        membership.role = data["role"]"
)
new_guard_2 = (
"    if request.method == "POST" and form.is_valid():\n"
"        data = form.cleaned_data\n"
"        if membership.user == request.user and data["role"] != "admin":\n"
"            messages.error(request, "You cannot change your own role from Administrator.")\n"
"            return redirect("member_list")\n"
"        membership.role = data["role"]"
)

if old_guard_2 not in text:
raise SystemExit("Guard 2 target not found. Aborting.")
text = text.replace(old_guard_2, new_guard_2, 1)

path.write_text(text)
print("All three patches applied to admin_views.py.")
ENDPATCH
echo "patch_views.py written. Lines: $(wc -l < patch_views.py)"

echo ""
echo "=== Setup complete. Next: run ./r4b_2_apply.sh ==="