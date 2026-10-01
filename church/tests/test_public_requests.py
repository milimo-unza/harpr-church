from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from church.forms import PublicRequestForm


def form_data(**overrides):
    today = timezone.localdate()
    data = {
        "submitter_name": "Test User",
        "submitter_contact": "0971234567",
        "title": "Test",
        "body": "Body text",
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=7)).isoformat(),
    }
    data.update(overrides)
    return data


class PublicRequestValidationTests(TestCase):
    # Only the basic cases automated. The rest of the phone rules
    # (international format, spaces, dashes) were tested by hand.

    def test_valid_phone_passes(self):
        f = PublicRequestForm(data=form_data())
        self.assertTrue(f.is_valid())

    def test_garbage_contact_fails(self):
        f = PublicRequestForm(data=form_data(submitter_contact="abc"))
        self.assertFalse(f.is_valid())

    def test_end_before_start_fails(self):
        today = timezone.localdate()
        f = PublicRequestForm(data=form_data(
            start_date=(today + timedelta(days=10)).isoformat(),
            end_date=today.isoformat(),
        ))
        self.assertFalse(f.is_valid())
