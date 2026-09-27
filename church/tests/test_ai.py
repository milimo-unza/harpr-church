from django.test import TestCase

from church.models import Church
from church.views.admin_views import gather_church_stats


class AIStatsTests(TestCase):
    def test_stats_keys_are_stable(self):
        church = Church.objects.create(name="Test Church", slug="test-ai")
        stats = gather_church_stats(church)
        self.assertEqual(
            set(stats),
            {
                "service_count",
                "avg_delay_minutes",
                "avg_overrun_minutes",
                "most_delayed_item",
                "overrun_count",
            },
        )