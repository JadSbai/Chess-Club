"""Tests of apply club view"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages



class AcknowledgeViewTestCase(TestCase):
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
        self.url = reverse('apply_club', kwargs={'club_name': self.club.name})
        # self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_acknowledged_url(self):
        self.assertEqual(self.url, f'/apply_club/{self.club.name}')

    def test_notification_sent_to_officers_and_owner_for_new_applicant(self):
        self.client.login(email=self.applicant.email, password='Password123')
        for member in self.club.members.all():
            if self.club.user_status(member) == "officer" or self.club.user_status(member) == "owner":
                notifications = len(member.notifications.unread())
                self.client.get(self.url)
                last_notification = member.notifications.unread()[0].description
                self.assertEqual(len(member.notifications.unread()), notifications + 1)
                self.assertEqual(last_notification, f"{self.applicant.full_name()} has applied to club {self.club.name}")
