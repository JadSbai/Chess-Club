"""Tests of the My Profile view."""
from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User
from chessclubs.tests.helpers import reverse_with_next


class MyProfileViewTestCase(TestCase):
    """Tests of the my_profile view."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.url = reverse('my_profile')

    def test_my_profile_url(self):
        self.assertEqual(self.url, '/my_profile/')

    def test_get_profile(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_profile.html')
        self.assertContains(response, f"{self.user.full_name()}", html=True)
        self.assertContains(response, f"Bio: {self.user.bio}", html=True)
        self.assertContains(response, f"Email: {self.user.email}", html=True)
        self.assertContains(response, f"Chess Experience: {self.user.chess_experience}", html=True)
        self.assertContains(response, f"Personal Statement: {self.user.personal_statement}", html=True)


    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
