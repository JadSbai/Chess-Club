"""Unit tests of acknowledged view """

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages



class AcknowledgeViewTestCase(TestCase):
    """Unit tests of acknowledged view """
    
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.applicant = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.client.login(email=self.club.owner.email, password='Password123')
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_applicant(self.applicant)
        self.accept_url = reverse('accept', kwargs={'club_name': self.club.name, 'user_id': self.applicant.id})
        self.deny_url = reverse('deny', kwargs={'club_name': self.club.name, 'user_id': self.applicant.id})
        self.url = reverse('acknowledge', kwargs={'club_name': self.club.name})
        self.redirect_url = reverse('show_club', kwargs={'club_name': self.club.name})

    def test_acknowledged_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/acknowledge/')

    def test_denied_applicant_becomes_non_member(self):
        self.client.get(self.deny_url)
        self.client.login(email=self.applicant.email, password='Password123')
        self.client.get(self.url)
        self.assertEqual(self.club.user_status(self.applicant), "authenticated_non_member_user")
        self.assertNotEqual(self.club.user_status(self.applicant), "denied_applicant")

    def test_notification_sent_to_officers_and_owner_for_accepted_applicant(self):
        self.client.get(self.accept_url)
        self.client.login(email=self.applicant.email, password='Password123')
        for member in self.club.members.all():
            if self.club.user_status(member) == "officer" or self.club.user_status(member) == "owner":
                notifications = len(member.notifications.unread())
                self.client.get(self.url)
                last_notification = member.notifications.unread()[0].description
                self.assertEqual(len(member.notifications.unread()), notifications + 1)
                self.assertEqual(last_notification, f"{self.applicant.full_name()} has joined club {self.club.name}")

    def test_mark_as_read_new_member(self):
        self.client.get(self.accept_url)
        self.client.login(email=self.applicant.email, password='Password123')
        self.client.get(self.url)
        self.client.login(email=self.club.owner.email, password='Password123')
        last_notification = self.club.owner.notifications.unread()[0]
        read_notif_url = reverse('mark_as_read', kwargs={'slug': last_notification.slug})
        members_list_url = reverse('user_list', kwargs={'club_name': self.club.name})
        response = self.client.get(read_notif_url, follow=True)
        self.assertRedirects(response, members_list_url, status_code=302, target_status_code=200)

    def test_accepted_applicant_becomes_member(self):
        self.client.get(self.accept_url)
        self.client.login(email=self.applicant.email, password='Password123')
        self.client.get(self.url)
        self.assertEqual(self.club.user_status(self.applicant), "member")
        self.assertNotEqual(self.club.user_status(self.applicant), "accepted_applicant")

    def test_redirects_to_club_when_accepted(self):
        self.target_url = reverse('show_club', kwargs={'club_name': self.club.name})
        self.client.get(self.accept_url)
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.target_url, status_code=302, target_status_code=200)

    def test_redirects_to_my_applications_when_accepted(self):
        self.target_url = reverse('my_applications')
        self.client.get(self.deny_url)
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.target_url, status_code=302, target_status_code=200)


    def test_applicant_cannot_acknowledge(self):
        self.group_tester.make_applicant(self.applicant)
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_accepted_applicant_can_acknowledge(self):
        self.group_tester.make_accepted_applicant(self.applicant)
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_denied_applicant_can_acknowledge(self):
        self.group_tester.make_denied_applicant(self.applicant)
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_member_cannot_acknowledge(self):
        self.group_tester.make_member(self.applicant)
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_officer_cannot_acknowledge(self):
        self.group_tester.make_officer(self.applicant)
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_owner_cannot_acknowledge(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_logged_in_non_member_cannot_acknowledge(self):
        self.group_tester.make_authenticated_non_member(self.applicant)
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_non_logged_is_redirected(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('acknowledge', kwargs={'club_name': self.club.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
