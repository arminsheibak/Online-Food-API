from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class TestUserAdmin(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@email.com", password="password123"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@email.com", password="password1234"
        )

    def test_users_are_listed_on_users_page(self):
        url = reverse("admin:users_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.email)

    def test_user_change_page_works(self):
        url = reverse("admin:users_user_change", args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_user_add_page(self):
        url = reverse("admin:users_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
