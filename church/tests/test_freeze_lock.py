from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from church.models import Church, Membership, Service, ServiceItem
from church.services.recalculation import freeze_service


class FreezeLockTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("coordinator", password="test")
        self.church = Church.objects.create(name="Test", slug="test-lock")
        Membership.objects.create(user=self.user, church=self.church, role="admin")
        self.service = Service.objects.create(
            church=self.church,
            name="Sunday",
            date=timezone.localdate(),
            status="draft",
        )
        self.item = ServiceItem.objects.create(
            service=self.service,
            order=0,
            title="Sermon",
            planned_start=timezone.now(),
            planned_duration_minutes=30,
        )
        self.client.force_login(self.user)

    def test_cannot_add_item_to_frozen_service(self):
        freeze_service(self.service, self.user)
        response = self.client.post(
            f"/services/{self.service.pk}/items/new/",
            {
                "title": "New item",
                "planned_start": timezone.now().strftime("%Y-%m-%dT%H:%M"),
                "planned_duration_minutes": "10",
            },
        )
        # Non-AJAX returns redirect with error message.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.service.items.count(), 1)

    def test_cannot_delete_item_from_frozen_service(self):
        freeze_service(self.service, self.user)
        response = self.client.post(
            f"/services/{self.service.pk}/items/{self.item.pk}/delete/",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.service.items.count(), 1)

    def test_can_delete_item_from_draft_service(self):
        response = self.client.post(
            f"/services/{self.service.pk}/items/{self.item.pk}/delete/",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.service.items.count(), 0)
