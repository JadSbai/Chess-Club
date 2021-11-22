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
        self.user = User.objects.get(email='johndoe@example.org')
        self.user2 = User.objects.get(email = 'janedoe@example.org')
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester = GroupTester()
        self.group_tester.make_applicant(self.user2)
        self.group_tester.make_officer(self.user)
        self.url = reverse('acknowledged')

    def test_acknowledged_url(self):
        self.assertEqual(self.url, '/acknowledged/')

    def test_acknowledged_is_no_more_applicant_deny(self):
        self.assertFalse(self.user2.groups.filter(name="denied_applicants").exists())

    def test_redirect_to_home_page(self):
        self.target_url = reverse('home')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.target_url, status_code=302, target_status_code=200)