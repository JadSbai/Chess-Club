"""Tests of promote view."""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from django.contrib import messages
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from django.core.exceptions import ObjectDoesNotExist
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN


class PromoteViewTestCase(TestCase):
    """Test suites for the Promote view"""
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.other_user = User.objects.get(email='petrapickles@example.org')
        self.client.login(email=self.owner.email, password='Password123')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_member(self.member)
        self.url = reverse('promote', kwargs={'club_name': self.club.name, 'user_id': self.member.id})
        self.show_self = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.owner.id})
        self.redirect_url = reverse('show_club', kwargs={'club_name': self.club.name})

    def test_promote_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/promote/{self.member.id}')

    def test_member_is_promoted_to_officer(self):
        before_status = self.club.user_status(self.member)
        self.assertEqual(before_status, "member")
        self.client.get(self.url)
        after_status = self.club.user_status(self.member)
        self.assertEqual(after_status, "officer")

    def test_member_receives_notification_of_promotion(self):
        notifications = len(self.member.notifications.unread())
        self.client.get(self.url)
        last_notification = self.member.notifications.unread()[0].description
        self.assertEqual(len(self.member.notifications.unread()), notifications + 1)
        self.assertEqual(last_notification, f"You have been promoted to Officer of club {self.club.name}")

    def test_mark_as_read_promote(self):
        self.client.get(self.url)
        last_notification = self.member.notifications.unread()[0]
        read_notif_url = reverse('mark_as_read', kwargs={'slug': last_notification.slug})
        show_club_url = reverse('show_club', kwargs={'club_name': self.club.name})
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(read_notif_url, follow=True)
        self.assertRedirects(response, show_club_url, status_code=302, target_status_code=200)

    def test_successful_promote_redirects(self):
        response = self.client.get(self.url)
        target_url = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.member.id})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)

    def test_forbidden_promote_redirects(self):
        self.group_tester.make_officer(self.member)
        before_status = self.club.user_status(self.member)
        response = self.client.get(self.url)
        after_status = self.club.user_status(self.member)
        self.assertEqual(after_status, before_status)
        target_url = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.member.id})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)

    def test_wrong_user_promote(self):
        bad_url = reverse('promote', kwargs={'club_name': self.club.name, 'user_id': 2000})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('user_list', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The user you are looking for does not exist!")

    def test_wrong_club_promote(self):
        bad_url = reverse('promote', kwargs={'club_name': "blabla", 'user_id': self.member.id})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_cannot_promote_yourself(self):
        own_url = reverse('promote', kwargs={'club_name': self.club.name, 'user_id': self.club.owner.id})
        response = self.client.get(own_url, follow=True)
        self.assertRedirects(response, self.show_self, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_applicant_cannot_promote(self):
        self.group_tester.make_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_accepted_applicant_cannot_promote(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_denied_applicant_cannot_promote(self):
        self.group_tester.make_denied_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_member_cannot_promote(self):
        self.group_tester.make_member(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_officer_cannot_promote(self):
        self.group_tester.make_officer(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_owner_can_promote(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_logged_in_non_member_cannot_promote(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_non_logged_is_redirected(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('promote', kwargs={'club_name': self.club.name, 'user_id': self.member.id}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)





