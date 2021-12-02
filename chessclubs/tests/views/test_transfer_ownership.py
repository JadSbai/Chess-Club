"""Tests of transfer ownership view."""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from django.contrib import messages
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from django.core.exceptions import ObjectDoesNotExist
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN

class TransferOwnershipViewTestCase(TestCase):
    """Test suites for transfer ownership view"""
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.other_user = User.objects.get(email='petrapickles@example.org')
        self.officer = User.objects.get(email='janedoe@example.org')
        self.client.login(email=self.owner.email, password='Password123')
        self.club = Club.objects.create(name="Club1", location="London", description="Yo", owner=self.owner)
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_officer(self.officer)
        self.url = reverse('transfer_ownership', kwargs={'club_name': self.club.name, 'user_id': self.officer.id})
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_transfer_ownership_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/transfer_ownership/{self.officer.id}')

    def test_successful_transfer(self):
        before_status = self.club.user_status(self.officer)
        before_count = self.club.officer_count()
        self.assertEqual(before_status, "officer")
        before_status = self.club.user_status(self.owner)
        self.assertEqual(before_status, "owner")
        self.form_input = {'owner': 'janedoe@example.org'}
        self.client.post(self.url, follow=True)
        after_status = self.club.user_status(self.officer)
        self.assertEqual(after_status, "owner")
        after_status = self.club.user_status(self.owner)
        self.assertEqual(after_status, "officer")
        self.assertEqual(self.club.owner_count(), 1)
        self.assertEqual(self.club.officer_count(), before_count)

    def test_officer_receives_notification_of_transfer(self):
        notifications = len(self.officer.notifications.unread())
        self.client.get(self.url)
        last_notification = self.officer.notifications.unread()[0].description
        self.assertEqual(len(self.officer.notifications.unread()), notifications + 1)
        self.assertEqual(last_notification, f"You have been transferred the ownership of the club {self.club.name}")

    def test_successful_transfer_redirects(self):
        response = self.client.get(self.url)
        target_url = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.officer.id})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)

    def test_forbidden_transfer_redirects(self):
        self.group_tester.make_member(self.officer)
        before_status = self.club.user_status(self.officer)
        response = self.client.get(self.url)
        after_status = self.club.user_status(self.officer)
        self.assertEqual(after_status, before_status)
        target_url = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.officer.id})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)

    def test_wrong_user_or_club_transfer(self):
        bad_url = reverse('transfer_ownership', kwargs={'club_name': "blabla", 'user_id': 2000})
        with self.assertRaises(ObjectDoesNotExist):
            response = self.client.get(bad_url)
            target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
            self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
            messages_list = list(response.context['messages'])
            self.assertEqual(len(messages_list), 1)
            self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_applicant_cannot_transfer(self):
        self.group_tester.make_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_accepted_applicant_cannot_transfer(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_denied_applicant_cannot_transfer(self):
        self.group_tester.make_denied_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_member_cannot_transfer(self):
        self.group_tester.make_member(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_officer_cannot_transfer(self):
        self.group_tester.make_officer(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_owner_can_transfer(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_logged_in_non_member_cannot_transfer(self):
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
        redirect_url = reverse_with_next('log_in', reverse('transfer_ownership', kwargs={'club_name': self.club.name, 'user_id': self.officer.id}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)





