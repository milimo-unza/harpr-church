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
    help = "Create or update the Harpr Church demonstration data."

    def handle(self, *args, **options):
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
        for slug, name in [
            ("pastors", "Pastors"),
            ("music", "Music"),
            ("ushering", "Ushering"),
            ("media", "Media"),
            ("children", "Children"),
            ("prayer", "Prayer"),
        ]:
            departments[slug], _ = Department.objects.update_or_create(
                church=church,
                slug=slug,
                defaults={"name": name, "color": "#b5623e"},
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
            user = self._user(username, f"{username}@example.com", username.title(), "Head")
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

        sunday = timezone.localdate() - timedelta(days=(timezone.localdate().weekday() + 1) % 7)
        names = {
            "Sermon": ["Pastor Phiri", "Pastor Banda", "Pastor Mulenga"],
            "Worship Songs": ["Ruth Mwansa", "Mwaka Zulu", "Chanda Tembo"],
            "Offering": ["Moses Lungu", "Esther Chileshe", "Andrew Sakala"],
            "Scripture Reading": ["Grace Mumba", "Brian Kunda", "Naomi Sampa"],
        }
        valid_service_dates = [
            sunday + timedelta(days=week * 7) for week in range(-3, 5)
        ]
        Service.objects.filter(
            church=church,
            name="Sunday Worship Service",
        ).exclude(date__in=valid_service_dates).delete()
        for service_index, service_date in enumerate(valid_service_dates):
            service, _ = Service.objects.update_or_create(
                church=church,
                date=service_date,
                name="Sunday Worship Service",
                defaults={"template": template, "status": "draft"},
            )
            start = timezone.make_aware(datetime.combine(service_date, time(8, 0)))
            for order, (title, duration, department_slug) in enumerate(item_specs):
                item, _ = ServiceItem.objects.update_or_create(
                    service=service,
                    order=order,
                    defaults={
                        "title": title,
                        "planned_start": start,
                        "planned_duration_minutes": duration,
                        "responsible_department": departments[department_slug],
                        "status": "planned",
                    },
                )
                if title in names:
                    from church.models import Assignment

                    Assignment.objects.update_or_create(
                        service_item=item,
                        person_name=names[title][service_index % len(names[title])],
                        role=title,
                        defaults={"church": church},
                    )
                start += timedelta(minutes=duration)

        event_specs = [
            ("Choir Practice", "rehearsal", 2, time(18, 0), time(19, 30), "music"),
            ("Bible Study", "study", 4, time(18, 30), time(20, 0), "pastors"),
            ("Youth Meeting", "meeting", 5, time(14, 0), time(16, 0), "children"),
            ("Prayer Meeting", "meeting", 5, time(9, 0), time(11, 0), "prayer"),
            ("Media Team Rehearsal", "rehearsal", 1, time(17, 0), time(18, 0), "media"),
        ]
        monday = timezone.localdate() - timedelta(days=timezone.localdate().weekday())
        for title, event_type, day_offset, start_time, end_time, department_slug in event_specs:
            ChurchEvent.objects.update_or_create(
                church=church,
                title=title,
                date=monday + timedelta(days=day_offset),
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
            title="Welcome to Sunday worship",
            defaults={
                "body": "Please arrive ten minutes early for worship.",
                "show_on_public": True,
                "is_active": True,
            },
        )
        Announcement.objects.update_or_create(
            church=church,
            title="Community outreach",
            defaults={
                "body": "The church family meets after service for the monthly outreach briefing.",
                "show_on_public": True,
                "is_active": True,
            },
        )
        self.stdout.write(self.style.SUCCESS("Harpr Church demo data is ready."))
        self.stdout.write("Coordinator: coordinator / harpr2026")
        self.stdout.write("Department heads: music_head, pastors_head, ushering_head, media_head / harpr2026")
        self.stdout.write("Public URL: /c/grace-covenant/")

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