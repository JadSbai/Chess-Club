"""Tests of leave club view"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages


class LeaveClubViewTestCase(TestCase):
    """Test Suites of leave club view"""
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.member = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.client.login(email=self.member.email, password='Password123')
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_member(self.member)
        self.url = reverse('leave', kwargs={'club_name': self.club.name})
        self.redirect_url = reverse('show_club', kwargs={'club_name': self.club.name})

    def test_leave_club_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/leave/')

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('leave', kwargs={'club_name': self.club.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_notification_sent_to_officers_and_owner(self):
        for member in self.club.members.all():
            if self.club.user_status(member) == "officer" or self.club.user_status(member) == "owner":
                notifications = len(member.notifications.unread())
                self.client.get(self.url)
                last_notification = member.notifications.unread()[0].description
                self.assertEqual(len(member.notifications.unread()), notifications + 1)
                self.assertEqual(last_notification, f"{self.member.full_name()} has left club {self.club.name}")

    def test_notification_of_leave_sent(self):
        notifications = len(self.member.notifications.unread())
        self.client.get(self.url)
        last_notification = self.member.notifications.unread()[0].description
        self.assertEqual(len(self.member.notifications.unread()), notifications+1)
        self.assertEqual(last_notification, f"You have left {self.club.name}")

    def test_mark_as_read_leave(self):
        self.client.get(self.url)
        last_notification = self.member.notifications.unread()[0]
        read_notif_url = reverse('mark_as_read', kwargs={'slug': last_notification.slug})
        show_club_url = reverse('show_club', kwargs={'club_name': self.club.name})
        response = self.client.get(read_notif_url, follow=True)
        self.assertRedirects(response, show_club_url, status_code=302, target_status_code=200)

    def test_mark_as_read_leave_notice(self):
        self.client.get(self.url)
        self.client.login(email=self.club.owner.email, password='Password123')
        last_notification = self.club.owner.notifications.unread()[0]
        read_notif_url = reverse('mark_as_read', kwargs={'slug': last_notification.slug})
        show_club_url = reverse('user_list', kwargs={'club_name': self.club.name})
        response = self.client.get(read_notif_url, follow=True)
        self.assertRedirects(response, show_club_url, status_code=302, target_status_code=200)

    def test_becomes_non_member_of_club(self):
        before_status = self.club.user_status(self.member)
        self.assertEqual(before_status, "member")
        self.client.get(self.url)
        after_status = self.club.user_status(self.member)
        self.assertEqual(after_status, "authenticated_non_member_user")

    def test_successful_leave_redirects(self):
        response = self.client.get(self.url)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)

    def test_wrong_club_leave(self):
        bad_url = reverse('leave', kwargs={'club_name': "blabla"})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_applicant_cannot_leave(self):
        self.group_tester.make_applicant(self.member)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_accepted_applicant_cannot_leave(self):
        self.group_tester.make_accepted_applicant(self.member)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_denied_applicant_cannot_leave(self):
        self.group_tester.make_denied_applicant(self.member)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_member_can_leave(self):
        self.group_tester.make_member(self.member)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_officer_can_leave(self):
        self.group_tester.make_officer(self.member)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_owner_cannot_leave(self):
        self.client.login(email=self.club.owner.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_logged_in_non_member_cannot_leave(self):
        self.group_tester.make_authenticated_non_member(self.member)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    # Thorough tests for template content

