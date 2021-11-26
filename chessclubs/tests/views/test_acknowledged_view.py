"""Tests of acknowledged"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User
from chessclubs.tests.helpers import GroupTester




class AcknowledgedViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json'
                ]

    def setUp(self):
        self.denied_applicant = User.objects.get(email='janedoe@example.org')
        self.client.login(email=self.denied_applicant.email, password='Password123')
        self.group_tester = GroupTester()
        self.group_tester.make_denied_applicant(self.denied_applicant)
        self.url = reverse('acknowledged')

    def test_acknowledged_url(self):
        self.assertEqual(self.url, '/acknowledged/')

    def test_becomes_non_member(self):
        self.assertFalse(self.denied_applicant.status() == "authenticated_non_member_user")

    def test_redirect_to_home_page(self):
        self.target_url = reverse('home')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.target_url, status_code=302, target_status_code=200)
