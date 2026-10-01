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
    def test_valid_10_digit_phone(self):
        f = PublicRequestForm(data=form_data(submitter_contact="0971234567"))
        self.assertTrue(f.is_valid(), f.errors)

    def test_valid_email(self):
        f = PublicRequestForm(data=form_data(submitter_contact="a@b.com"))
        self.assertTrue(f.is_valid(), f.errors)

    def test_valid_international(self):
        f = PublicRequestForm(data=form_data(submitter_contact="+260971234567"))
        self.assertTrue(f.is_valid(), f.errors)

    def test_short_phone_rejected(self):
        f = PublicRequestForm(data=form_data(submitter_contact="09712345"))
        self.assertFalse(f.is_valid())
        self.assertIn("submitter_contact", f.errors)

    def test_long_phone_rejected(self):
        f = PublicRequestForm(data=form_data(submitter_contact="09712345678"))
        self.assertFalse(f.is_valid())

    def test_garbage_rejected(self):
        f = PublicRequestForm(data=form_data(submitter_contact="abc"))
        self.assertFalse(f.is_valid())

    def test_end_before_start_rejected(self):
        today = timezone.localdate()
        f = PublicRequestForm(data=form_data(
            start_date=(today + timedelta(days=10)).isoformat(),
            end_date=today.isoformat(),
        ))
        self.assertFalse(f.is_valid())

    def test_missing_name_rejected(self):
        f = PublicRequestForm(data=form_data(submitter_name=""))
        self.assertFalse(f.is_valid())

    def test_missing_dates_rejected(self):
        f = PublicRequestForm(data=form_data(start_date="", end_date=""))
        self.assertFalse(f.is_valid())
