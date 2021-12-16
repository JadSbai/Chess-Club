"""Tests of my applications view"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from with_asserts.mixin import AssertHTMLMixin


class MyApplicationsViewTestCase(TestCase, AssertHTMLMixin):
    """Test Suites of my applications view"""
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.applicant = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.client.login(email=self.applicant.email, password='Password123')
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_authenticated_non_member(self.applicant)
        self.url = reverse('my_applications')
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_my_applications_url(self):
        self.assertEqual(self.url, f'/my_applications/')

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('my_applications'))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_no_application_display(self):
        response = self.client.get(self.url)
        self.assertContains(response, "You currently have no application undergoing.")

    def test_pending_application_display(self):
        self.group_tester.make_applicant(self.applicant)
        response = self.client.get(self.url)
        with self.assertHTML(response, element_id="under_review") as accept:
            self.assertEqual(accept.text, "Notice: Your application is now under review.")

    def test_accepted_application_display(self):
        self.group_tester.make_accepted_applicant(self.applicant)
        response = self.client.get(self.url)
        with self.assertHTML(response, element_id="accepted") as accept:
            self.assertEqual(accept.text, "Notice: Your application has been accepted")
        self.assertContains(response, "Join now!", html=True)

    def test_denied_application_display(self):
        self.group_tester.make_denied_applicant(self.applicant)
        response = self.client.get(self.url)
        with self.assertHTML(response, element_id="denied") as accept:
            self.assertEqual(accept.text, "Notice: Your application has been denied.")
        self.assertContains(response, "OK")

    # Thorough tests for template content
