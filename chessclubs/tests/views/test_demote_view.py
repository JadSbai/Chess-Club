"""Tests of demote view."""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from django.contrib import messages
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from django.core.exceptions import ObjectDoesNotExist
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN

class DemoteViewTestCase(TestCase):
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
        self.show_self = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.owner.id})
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_demote_url(self):
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

    def test_forbidden_demote_redirects(self):
        self.group_tester.make_member(self.officer)
        before_status = self.club.user_status(self.officer)
        response = self.client.get(self.url)
        after_status = self.club.user_status(self.officer)
        self.assertEqual(after_status, before_status)
        target_url = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.officer.id})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)

    def test_wrong_user_demote(self):
        bad_url = reverse('demote', kwargs={'club_name': self.club.name, 'user_id': 2000})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('user_list', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The user you are looking for does not exist!")

    def test_wrong_club_demote(self):
        bad_url = reverse('demote', kwargs={'club_name': "blabla", 'user_id': self.officer.id})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_cannot_demote_yourself(self):
        own_url = reverse('demote', kwargs={'club_name': self.club.name, 'user_id': self.club.owner.id})
        response = self.client.get(own_url, follow=True)
        self.assertRedirects(response, self.show_self, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_applicant_cannot_demote(self):
        self.client.login(email=self.officer.email, password='Password123')
        self.group_tester.make_applicant(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_accepted_applicant_cannot_demote(self):
        self.client.login(email=self.officer.email, password='Password123')
        self.group_tester.make_accepted_applicant(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_denied_applicant_cannot_demote(self):
        self.client.login(email=self.officer.email, password='Password123')
        self.group_tester.make_denied_applicant(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_member_cannot_demote(self):
        self.client.login(email=self.officer.email, password='Password123')
        self.group_tester.make_member(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_officer_cannot_demote(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_owner_can_demote(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_logged_in_non_member_cannot_demote(self):
        self.client.login(email=self.officer.email, password='Password123')
        self.group_tester.make_authenticated_non_member(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_non_logged_is_redirected(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('demote', kwargs={'club_name': self.club.name, 'user_id': self.officer.id}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # Forbidden ban test only covers the case where you try to ban an officer, similar tests should be written for all other statuses





