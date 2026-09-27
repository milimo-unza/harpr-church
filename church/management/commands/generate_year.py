"""Generate a full year of services from active templates."""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from church.models import (
    Church, Service, ServiceItem, ServiceTemplate,
)


class Command(BaseCommand):
    help = "Generate a year of services for a church from its active templates."

    def add_arguments(self, parser):
        parser.add_argument("--church", required=True, help="Church slug")
        parser.add_argument("--year", type=int, default=date.today().year)

    def handle(self, *args, **options):
        try:
            church = Church.objects.get(slug=options["church"])
        except Church.DoesNotExist:
            self.stderr.write(f"No church with slug '{options['church']}'")
            return

        year = options["year"]
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        created = 0

        for template in church.service_templates.filter(is_active=True):
            target_weekday = template.day_of_week
            d = start
            while d <= end:
                if d.weekday() == target_weekday:
                    service, was_created = Service.objects.get_or_create(
                        church=church, template=template, date=d,
                        defaults={"name": template.name, "status": "draft"},
                    )
                    if was_created:
                        start_dt = timezone.make_aware(
                            # Use template default start time on the date
                            timezone.datetime.combine(
                                d, template.default_start_time)
                        )
                        # Create service items from template items
                        for item in template.items.all():
                            ServiceItem.objects.create(
                                service=service,
                                order=item.order,
                                title=item.title,
                                planned_start=start_dt,
                                planned_duration_minutes=item.default_duration_minutes,
                                responsible_department=item.responsible_department,
                                notes=item.notes,
                            )
                        created += 1
                d += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(
            f"Created {created} service(s) for {church.name} in {year}."
        ))
