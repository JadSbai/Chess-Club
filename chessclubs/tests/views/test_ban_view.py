"""Tests of the ban member view."""
from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages


class BanViewTestCase(TestCase):
    """Test Suites of the ban member view."""

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.club = Club.objects.get(name="Test_Club")
        self.owner = self.club.owner
        self.member = User.objects.get(email="janedoe@example.org")
        self.other_member = User.objects.get(email="petrapickles@example.org")
        self.client.login(email=self.owner.email, password='Password123')
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_member(self.member)
        self.group_tester.make_member(self.other_member)
        self.url = reverse('ban', kwargs={'club_name': self.club.name, 'user_id': self.member.id})
        self.secondary_url = reverse('ban', kwargs={'club_name': self.club.name, 'user_id': self.other_member.id})
        self.show_self = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.owner.id})
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_ban_member_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/ban/{self.member.id}')

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('ban', kwargs={'club_name': self.club.name, 'user_id': self.member.id}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_notification_of_ban_sent(self):
        notifications = len(self.member.notifications.unread())
        self.client.get(self.url)
        last_notification = self.member.notifications.unread()[0].description
        self.assertEqual(len(self.member.notifications.unread()), notifications+1)
        self.assertEqual(last_notification, f"You have been banned from {self.club.name}")

    def test_becomes_non_member_of_club(self):
        before_status = self.club.user_status(self.member)
        self.assertEqual(before_status, "member")
        self.client.get(self.url)
        after_status = self.club.user_status(self.member)
        self.assertEqual(after_status, "authenticated_non_member_user")

    def test_successful_ban_redirects(self):
        response = self.client.get(self.url)
        target_url = reverse('user_list', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)

    def test_wrong_club_ban(self):
        bad_url = reverse('ban', kwargs={'club_name': "blabla", 'user_id': self.member.id})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_wrong_user_ban(self):
        bad_url = reverse('ban', kwargs={'club_name': self.club.name, 'user_id': 2000})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('user_list', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The user you are looking for does not exist!")

    def test_forbidden_ban_redirects(self):
        self.group_tester.make_officer(self.member)
        before_status = self.club.user_status(self.member)
        response = self.client.get(self.url, follow=True)
        after_status = self.club.user_status(self.member)
        self.assertEqual(after_status, before_status)
        target_url = reverse('user_list', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_cannot_ban_yourself(self):
        own_url = reverse('ban', kwargs={'club_name': self.club.name, 'user_id': self.club.owner.id})
        response = self.client.get(own_url, follow=True)
        self.assertRedirects(response, self.show_self, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_applicant_cannot_ban(self):
        self.group_tester.make_applicant(self.member)
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.secondary_url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_accepted_applicant_cannot_ban(self):
        self.group_tester.make_accepted_applicant(self.member)
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.secondary_url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_denied_applicant_cannot_ban(self):
        self.group_tester.make_denied_applicant(self.member)
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.secondary_url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_member_cannot_ban(self):
        self.group_tester.make_member(self.member)
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.secondary_url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_officer_cannot_ban(self):
        self.group_tester.make_officer(self.member)
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.secondary_url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_owner_can_ban(self):
        self.client.login(email=self.club.owner.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_logged_in_non_member_cannot_ban(self):
        self.group_tester.make_authenticated_non_member(self.member)
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.secondary_url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    # Thorough tests for template content
    # Forbidden ban test only covers the case where you try to ban an officer, similar tests should be written for all other statuses

