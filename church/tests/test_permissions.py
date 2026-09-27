from django.contrib.auth.models import User
from django.test import Client, TestCase

from church.models import Church, Membership


class PermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user("admin", password="test")
        self.dept = User.objects.create_user("dept", password="test")
        self.outsider = User.objects.create_user("outsider", password="test")
        self.church = Church.objects.create(name="Test", slug="test")
        Membership.objects.create(user=self.admin, church=self.church, role="admin")
        Membership.objects.create(user=self.dept, church=self.church, role="dept_head")

    def test_public_page_has_no_login_requirement(self):
        response = self.client.get(f"/c/{self.church.slug}/")
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirects_to_login(self):
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_department_head_cannot_access_admin_dashboard(self):
        self.client.login(username="dept", password="test")
        self.assertEqual(self.client.get("/dashboard/").status_code, 403)

    def test_outsider_cannot_access_admin_dashboard(self):
        self.client.login(username="outsider", password="test")
        self.assertEqual(self.client.get("/dashboard/").status_code, 403)