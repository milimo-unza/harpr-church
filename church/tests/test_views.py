from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from church.models import Church, Membership, Service


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("coordinator", password="test")
        self.church = Church.objects.create(name="Test Church", slug="test-views")
        Membership.objects.create(user=self.user, church=self.church, role="admin")
        self.service = Service.objects.create(
            church=self.church,
            name="Sunday Worship",
            date=timezone.localdate(),
        )
        self.client.force_login(self.user)

    def test_service_list_renders(self):
        self.assertEqual(self.client.get("/services/").status_code, 200)

    def test_service_detail_renders(self):
        self.assertEqual(
            self.client.get(f"/services/{self.service.pk}/").status_code,
            200,
        )