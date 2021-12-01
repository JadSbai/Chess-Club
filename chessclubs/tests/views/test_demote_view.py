"""Tests of accept."""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from django.contrib import messages
from chessclubs.tests.helpers import ClubGroupTester
from django.core.exceptions import ObjectDoesNotExist

class AcceptViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.officer = User.objects.get(email='janedoe@example.org')
        self.client.login(email=self.owner.email, password='Password123')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_officer(self.officer)
        self.url = reverse('demote', kwargs={'club_name': self.club.name, 'user_id': self.officer.id})

    def test_accept_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/demote/{self.officer.id}')

    def test_officer_is_demoted_to_member(self):
        before_status = self.club.user_status(self.officer)
        self.assertEqual(before_status, "officer")
        self.client.get(self.url)
        after_status = self.club.user_status(self.officer)
        self.assertEqual(after_status, "member")

    def test_officer_receives_notification_of_demotion(self):
        notifications = len(self.officer.notifications.unread())
        self.client.get(self.url)
        last_notification = self.officer.notifications.unread()[0].description
        self.assertEqual(len(self.officer.notifications.unread()), notifications + 1)
        self.assertEqual(last_notification, f"You have been demoted to Member of club {self.club.name}")

    def test_successful_demote_redirects(self):
        response = self.client.get(self.url)
        target_url = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.officer.id})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)

    def test_unsuccessful_demote(self):
        self.group_tester.make_member(self.officer)
        response = self.client.get(self.url)
        target_url = reverse('user_list', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_wrong_user_or_club_demote(self):
        bad_url = reverse('demote', kwargs={'club_name': "blabla", 'user_id': 2000})
        with self.assertRaises(ObjectDoesNotExist):
            response = self.client.get(bad_url)
            target_url = reverse('landing_page')
            self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
            messages_list = list(response.context['messages'])
            self.assertEqual(len(messages_list), 1)
            self.assertEqual(messages_list[0].level, messages.ERROR)





