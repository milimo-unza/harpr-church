from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from church.models import (
    Announcement,
    Church,
    ChurchEvent,
    Department,
    Membership,
    Service,
    ServiceItem,
    ServiceItemTemplate,
    ServiceTemplate,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Create or update the Harpr Church demonstration data (Round 3 seeder)."

    def handle(self, *args, **options):
        # Use fixed dates for July → November 2026 per Round 3 specification
        church, _ = Church.objects.update_or_create(
            slug="grace-covenant",
            defaults={
                "name": "Grace Covenant Church",
                "timezone": "Africa/Lusaka",
                "address": "Lusaka, Zambia",
                "is_active": True,
            },
        )

        departments = {}
        for slug, name, color in [
            ("pastors", "Pastors", "#7a9c59"),
            ("music", "Music", "#b5623e"),
            ("ushering", "Ushering", "#4a90e2"),
            ("media", "Media", "#9b59b6"),
            ("children", "Children", "#f1c40f"),
            ("prayer", "Prayer", "#e67e22"),
        ]:
            departments[slug], _ = Department.objects.update_or_create(
                church=church,
                slug=slug,
                defaults={"name": name, "color": color},
            )

        coordinator = self._user(
            "coordinator", "coordinator@example.com", "Programme", "Coordinator"
        )
        Membership.objects.update_or_create(
            user=coordinator,
            church=church,
            defaults={"role": "admin", "department": None, "is_active": True},
        )

        heads = {
            "music_head": "music",
            "pastors_head": "pastors",
            "ushering_head": "ushering",
            "media_head": "media",
        }
        for username, department_slug in heads.items():
            user = self._user(
                username, f"{username}@example.com", username.replace("_", " ").title(), "Head")
            Membership.objects.update_or_create(
                user=user,
                church=church,
                defaults={
                    "role": "dept_head",
                    "department": departments[department_slug],
                    "is_active": True,
                },
            )

        template, _ = ServiceTemplate.objects.update_or_create(
            church=church,
            name="Sunday Worship Service",
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
        for order, (title, duration, department_slug) in enumerate(item_specs):
            ServiceItemTemplate.objects.update_or_create(
                template=template,
                order=order,
                defaults={
                    "title": title,
                    "default_duration_minutes": duration,
                    "responsible_department": departments[department_slug],
                    "notes": "",
                },
            )

        # Create weekly services from July through November 2026 on Sundays
        start_date = date(2026, 7, 5)  # first Sunday in July 2026
        end_date = date(2026, 11, 29)  # last Sunday in November 2026
        current = start_date
        Service.objects.filter(church=church, name="Sunday Worship Service").exclude(
            date__range=(start_date, end_date)).delete()
        names = {
            "Sermon": ["Pastor Phiri", "Pastor Banda", "Pastor Mulenga", "Pastor Chanda"],
            "Worship Songs": ["Ruth Mwansa", "Mwaka Zulu", "Chanda Tembo"],
            "Offering": ["Moses Lungu", "Esther Chileshe", "Andrew Sakala"],
            "Scripture Reading": ["Grace Mumba", "Brian Kunda", "Naomi Sampa"],
        }
        idx = 0
        while current <= end_date:
            service, _ = Service.objects.update_or_create(
                church=church,
                date=current,
                name="Sunday Worship Service",
                defaults={"template": template, "status": "completed" if current <
                          timezone.localdate() else "draft"},
            )
            start_dt = timezone.make_aware(
                datetime.combine(current, time(8, 0)))
            for order, (title, duration, department_slug) in enumerate(item_specs):
                planned = start_dt
                item, _ = ServiceItem.objects.update_or_create(
                    service=service,
                    order=order,
                    defaults={
                        "title": title,
                        "planned_start": planned,
                        "planned_duration_minutes": duration,
                        "responsible_department": departments[department_slug],
                        "status": "completed" if service.status == "completed" else "planned",
                    },
                )
                if title in names:
                    from church.models import Assignment

                    Assignment.objects.update_or_create(
                        service_item=item,
                        person_name=names[title][idx % len(names[title])],
                        role=title,
                        defaults={"church": church},
                    )
                start_dt += timedelta(minutes=duration)
            idx += 1
            current += timedelta(days=7)

        # Some weekly events across the same period
        event_specs = [
            ("Choir Practice", "rehearsal", 2, time(18, 0), time(19, 30), "music"),
            ("Bible Study", "study", 4, time(18, 30), time(20, 0), "pastors"),
            ("Youth Meeting", "meeting", 5, time(14, 0), time(16, 0), "children"),
            ("Prayer Meeting", "meeting", 5, time(9, 0), time(11, 0), "prayer"),
            ("Media Team Rehearsal", "rehearsal",
             1, time(17, 0), time(18, 0), "media"),
        ]
        # place these in the first full week of July 2026 and let them repeat weekly
        first_monday = start_date - timedelta(days=start_date.weekday())
        for title, event_type, day_offset, start_time, end_time, department_slug in event_specs:
            d = first_monday + timedelta(days=day_offset)
            ChurchEvent.objects.update_or_create(
                church=church,
                title=title,
                date=d,
                defaults={
                    "event_type": event_type,
                    "start_time": start_time,
                    "end_time": end_time,
                    "location": "Main church campus",
                    "responsible_department": departments[department_slug],
                },
            )

        Announcement.objects.update_or_create(
            church=church,
            body="Please arrive ten minutes early for worship.",
            defaults={
                "show_on_public": True,
                "is_active": True,
                "start_date": timezone.localdate(),
                "end_date": timezone.localdate() + timedelta(days=7),
            },
        )
        Announcement.objects.update_or_create(
            church=church,
            body="The church family meets after service for the monthly outreach briefing.",
            defaults={
                "show_on_public": True,
                "is_active": True,
                "start_date": timezone.localdate(),
                "end_date": timezone.localdate() + timedelta(days=14),
            },
        )
        self.stdout.write(self.style.SUCCESS("Harpr demo data rebuilt."))
        self.stdout.write("Coordinator: coordinator / harpr2026")
        self.stdout.write(
            "Run: python manage.py seed_demo to refresh this data.")

    @staticmethod
    def _user(username, email, first_name, last_name):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.set_password("harpr2026")
        user.save()
        return user
