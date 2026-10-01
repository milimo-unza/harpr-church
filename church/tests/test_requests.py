from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from church.models import (
    Announcement,
    Church,
    ChurchEvent,
    Membership,
    Request,
)


class RequestApprovalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("coordinator", password="test")
        self.church = Church.objects.create(name="Test", slug="test-req")
        Membership.objects.create(user=self.user, church=self.church, role="admin")
        self.client.force_login(self.user)
        today = timezone.localdate()

        self.announcement_req = Request.objects.create(
            church=self.church,
            type="announcement",
            title="Test announcement",
            body="Original wording",
            submitter_name="Visitor",
            submitter_contact="0971234567",
            start_date=today,
            end_date=today + timedelta(days=7),
            status="pending",
        )

        self.schedule_req = Request.objects.create(
            church=self.church,
            type="schedule",
            title="Band practice",
            body="Need the hall Friday",
            submitter_name="Visitor",
            submitter_contact="0971234567",
            start_date=today + timedelta(days=3),
            requested_start_time=time(18, 0),
            requested_end_time=time(20, 0),
            status="pending",
        )

    def test_approving_announcement_creates_announcement(self):
        response = self.client.post(
            f"/requests/{self.announcement_req.pk}/respond/",
            {
                "status": "approved",
                "approved_text": "Reworded text for public.",
                "request_type": "announcement",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Announcement.objects.count(), 1)
        ann = Announcement.objects.first()
        self.assertEqual(ann.body, "Reworded text for public.")

    def test_approving_schedule_creates_event(self):
        response = self.client.post(
            f"/requests/{self.schedule_req.pk}/respond/",
            {
                "status": "approved",
                "approved_text": "Notes",
                "request_type": "schedule",
                "event_date": (timezone.localdate() + timedelta(days=3)).isoformat(),
                "event_start": "18:00",
                "event_end": "20:00",
                "event_location": "Main hall",
                "event_department": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ChurchEvent.objects.count(), 1)
        ev = ChurchEvent.objects.first()
        self.assertEqual(ev.title, "Band practice")
        self.assertEqual(ev.start_time, time(18, 0))

    def test_announcement_approval_requires_wording(self):
        response = self.client.post(
            f"/requests/{self.announcement_req.pk}/respond/",
            {
                "status": "approved",
                "approved_text": "",
                "request_type": "announcement",
            },
        )
        # Non-AJAX invalid POST redirects back to the list with a flash.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Announcement.objects.count(), 0)
        # And the request should still be pending.
        self.announcement_req.refresh_from_db()
        self.assertEqual(self.announcement_req.status, "pending")

    def test_schedule_approval_allows_empty_notes(self):
        response = self.client.post(
            f"/requests/{self.schedule_req.pk}/respond/",
            {
                "status": "approved",
                "approved_text": "",
                "request_type": "schedule",
                "event_date": (timezone.localdate() + timedelta(days=3)).isoformat(),
                "event_start": "18:00",
                "event_end": "20:00",
                "event_location": "Main hall",
                "event_department": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ChurchEvent.objects.count(), 1)

    def test_rejecting_does_not_create_anything(self):
        self.client.post(
            f"/requests/{self.announcement_req.pk}/respond/",
            {
                "status": "rejected",
                "approved_text": "Not appropriate.",
                "request_type": "announcement",
            },
        )
        self.assertEqual(Announcement.objects.count(), 0)
        self.announcement_req.refresh_from_db()
        self.assertEqual(self.announcement_req.status, "rejected")
