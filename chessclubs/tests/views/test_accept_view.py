"""Tests of accept."""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages


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
        self.target_url = reverse('view_applications', kwargs={'club_name': self.club.name})
        self.show_self = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': self.officer.id})
        self.redirect_url = reverse('show_club', kwargs={'club_name': self.club.name})

    def test_accept_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/accept/{self.applicant.id}')

    def test_accept_and_become_accepted_applicant(self):
        before_status = self.club.user_status(self.applicant)
        self.assertEqual(before_status, "applicant")
        self.client.get(self.url)
        after_status = self.club.user_status(self.applicant)
        self.assertEqual(after_status, "accepted_applicant")
        self.assertTrue(self.applicant.groups.filter(name=f"{self.club.name}_accepted_applicants").exists())
        self.assertFalse(self.applicant.groups.filter(name=f"{self.club.name}_applicants").exists())

    def test_redirect_to_application_page(self):
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

    def test_mark_as_read_acceptance(self):
        self.client.get(self.url)
        last_notification = self.applicant.notifications.unread()[0]
        read_notif_url = reverse('mark_as_read', kwargs={'slug': last_notification.slug})
        my_applications_url = reverse('my_applications')
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(read_notif_url, follow=True)
        self.assertRedirects(response, my_applications_url, status_code=302, target_status_code=200)

    def test_accept_non_applicant_redirects(self):
        self.club.add_member(self.applicant)
        self.club.remove_from_applicants_group(self.applicant)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_wrong_user_accept(self):
        bad_url = reverse('accept', kwargs={'club_name': self.club.name, 'user_id': 2000})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('view_applications', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The user you are looking for does not exist!")

    def test_wrong_club_accept(self):
        bad_url = reverse('accept', kwargs={'club_name': "blabla", 'user_id': self.applicant.id})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_cannot_accept_yourself(self):
        own_url = reverse('accept', kwargs={'club_name': self.club.name, 'user_id': self.officer.id})
        response = self.client.get(own_url, follow=True)
        self.assertRedirects(response, self.show_self, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_applicant_cannot_accept(self):
        self.group_tester.make_applicant(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_accepted_applicant_cannot_accept(self):
        self.group_tester.make_accepted_applicant(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_denied_applicant_cannot_accept(self):
        self.group_tester.make_denied_applicant(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_member_cannot_accept(self):
        self.group_tester.make_member(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_officer_can_accept(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_owner_can_accept(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_logged_in_non_member_cannot_accept(self):
        self.group_tester.make_authenticated_non_member(self.officer)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_non_logged_is_redirected(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('accept', kwargs={'club_name': self.club.name, 'user_id': self.applicant.id}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
