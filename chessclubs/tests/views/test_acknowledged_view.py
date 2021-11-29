"""Tests of acknowledged"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester




class AcknowledgedViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.denied_applicant = User.objects.get(email='janedoe@example.org')
        self.client.login(email=self.denied_applicant.email, password='Password123')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_denied_applicant(self.denied_applicant)
        self.url = reverse('acknowledged', kwargs={'club_name': self.club.name})

    def test_acknowledged_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/acknowledged/')

    def test_becomes_non_member(self):
        self.assertFalse(self.club.user_status(self.denied_applicant) == "authenticated_non_member_user")

    # def test_redirect_to_landing_page(self):
    #     self.target_url = reverse('landing_page')
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, self.target_url, status_code=302, target_status_code=200)
