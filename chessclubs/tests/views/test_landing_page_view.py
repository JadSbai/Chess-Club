"""Tests of landing page view"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages


class LandingPageViewTestCase(TestCase):
    """Test Suites of landing page view"""
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_authenticated_non_member(self.user)
        self.url = reverse('landing_page')
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_landing_page_url(self):
        self.assertEqual(self.url, f'/landing_page/')

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('landing_page'))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_base_display(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Name", html=True)
        self.assertContains(response, "Location", html=True)
        self.assertContains(response, "Create Club", html=True)

    # Thorough tests for template content

