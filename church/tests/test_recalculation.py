from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from church.models import Church, Membership, Service, ServiceItem
from church.services.recalculation import recalculate_times


class RecalculationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", password="test")
        self.church = Church.objects.create(name="Test", slug="test")
        Membership.objects.create(
            user=self.user, church=self.church, role="admin"
        )
        self.service = Service.objects.create(
            church=self.church,
            name="Test Service",
            date=timezone.localdate(),
        )
        base = timezone.make_aware(
            datetime(2026, 10, 5, 8, 0),
            timezone.get_current_timezone(),
        )
        self.items = []
        for i in range(4):
            item = ServiceItem.objects.create(
                service=self.service,
                order=i,
                title=f"Item {i}",
                planned_start=base + timedelta(minutes=i * 15),
                planned_duration_minutes=15,
            )
            self.items.append(item)

    def test_shifts_subsequent_items(self):
        new_start = self.items[0].planned_start + timedelta(minutes=23)
        changed = recalculate_times(
            self.service,
            self.items[0],
            new_start,
            user=self.user,
            reason="Late start",
        )
        self.assertEqual(len(changed), 4)
        self.items[0].refresh_from_db()
        self.items[1].refresh_from_db()
        self.assertEqual(self.items[0].actual_start, new_start)
        self.assertEqual(
            self.items[1].actual_start,
            self.items[1].planned_start + timedelta(minutes=23),
        )

    def test_respects_locked_items(self):
        self.items[2].lock_actual_start = True
        self.items[2].save()
        new_start = self.items[0].planned_start + timedelta(minutes=30)
        recalculate_times(
            self.service,
            self.items[0],
            new_start,
            user=self.user,
            reason="Test lock",
        )
        self.items[2].refresh_from_db()
        self.assertIsNone(self.items[2].actual_start)

    def test_respects_completed_items(self):
        self.items[1].status = "completed"
        self.items[1].actual_start = self.items[1].planned_start
        self.items[1].save()
        new_start = self.items[0].planned_start + timedelta(minutes=45)
        recalculate_times(
            self.service,
            self.items[0],
            new_start,
            user=self.user,
            reason="Test completed",
        )
        self.items[1].refresh_from_db()
        self.assertEqual(self.items[1].actual_start, self.items[1].planned_start)