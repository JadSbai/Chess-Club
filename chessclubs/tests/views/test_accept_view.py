"""Tests of accept."""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import reverse_with_next
from chessclubs.tests.helpers import ClubGroupTester
from notifications.models import Notification
from notifications.signals import notify

class AcceptViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.officer = User.objects.get(email='petrapickles@example.org')
        self.applicant = User.objects.get(email='janedoe@example.org')
        self.client.login(email=self.officer.email, password='Password123')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_applicant(self.applicant)
        self.group_tester.make_officer(self.officer)
        self.client.login(email=self.officer.email, password='Password123')
        self.url = reverse('accept', kwargs={'club_name': self.club.name, 'user_id': self.applicant.id})

    def test_accept_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/accept/{self.applicant.id}')

    def test_accept_and_become_member(self):
        before_status = self.club.user_status(self.applicant)
        self.assertEqual(before_status, "applicant")
        self.client.get(self.url)
        after_status = self.club.user_status(self.applicant)
        self.assertEqual(after_status, "member")
        self.assertTrue(self.applicant.groups.filter(name=f"{self.club.name}_members").exists())
        self.assertFalse(self.applicant.groups.filter(name=f"{self.club.name}_applicants").exists())

    def test_redirect_to_application_page(self):
        self.target_url = reverse('view_applications', kwargs={'club_name': self.club.name})
        response = self.client.get(self.url)
        self.assertRedirects(response, self.target_url, status_code=302, target_status_code=200)

    def test_number_of_applications_decremented(self):
        before = self.club.applicants_group().user_set.count()
        self.client.get(self.url)
        after = self.club.applicants_group().user_set.count()
        self.assertEqual(after, before - 1)

    def test_notification_sent(self):
        notifications = len(self.applicant.notifications.unread())
        self.client.get(self.url)
        last_notification = self.applicant.notifications.unread()[0].description
        self.assertEqual(len(self.applicant.notifications.unread()), notifications+1)
        self.assertEqual(last_notification, f"Your application for club {self.club.name} has been accepted")
