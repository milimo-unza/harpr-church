from django.test import TestCase
from django.utils import timezone

from church.models import Church, Service
from church.services.pdf import generate_bulletin_pdf


class PDFTests(TestCase):
    def test_pdf_starts_with_pdf_signature(self):
        church = Church.objects.create(name="Test Church", slug="test-pdf")
        service = Service.objects.create(
            church=church,
            name="Sunday Worship",
            date=timezone.localdate(),
        )
        buffer = generate_bulletin_pdf(service)
        self.assertTrue(buffer.read().startswith(b"%PDF"))