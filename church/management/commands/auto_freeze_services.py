from django.core.management.base import BaseCommand
from django.utils import timezone

from church.models import Service
from church.services.recalculation import freeze_service


class Command(BaseCommand):
    help = "Freeze all services for today that have not been frozen yet."

    def handle(self, *args, **options):
        services = Service.objects.filter(date=timezone.localdate(), status="draft")
        count = 0
        for service in services.select_related("church"):
            admin_membership = service.church.memberships.filter(role="admin").first()
            if admin_membership:
                freeze_service(
                    service,
                    admin_membership.user,
                    reason="Auto-frozen at midnight",
                )
                count += 1
        self.stdout.write(f"Froze {count} service(s).")