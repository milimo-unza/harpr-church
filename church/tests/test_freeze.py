from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from church.models import Church, Membership, Service
from church.services.recalculation import freeze_service, unfreeze_service


class FreezeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", password="test")
        self.church = Church.objects.create(name="Test", slug="test")
        Membership.objects.create(user=self.user, church=self.church, role="admin")
        self.service = Service.objects.create(
            church=self.church,
            name="Test Service",
            date=timezone.localdate(),
        )

    def test_freeze_creates_bulletin(self):
        bulletin = freeze_service(self.service, self.user)
        self.assertIsNotNone(bulletin)
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "frozen")
        self.assertEqual(bulletin.version, 1)

    def test_refreeze_creates_new_version(self):
        freeze_service(self.service, self.user)
        unfreeze_service(self.service, self.user, reason="Emergency change")
        bulletin = freeze_service(self.service, self.user)
        self.assertEqual(bulletin.version, 2)

    def test_unfreeze_requires_reason(self):
        freeze_service(self.service, self.user)
        with self.assertRaises(ValueError):
            unfreeze_service(self.service, self.user, reason="")
        unfreeze_service(self.service, self.user, reason="Test reason")
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "draft")
        self.assertEqual(self.service.unfrozen_reason, "Test reason")