"""Tests of my add_co_organiser view"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next, TournamentGroupTester, _create_test_players, \
    enter_results_to_all_matches
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages
from with_asserts.mixin import AssertHTMLMixin


class AddCoOrganiserViewTestCase(TestCase, AssertHTMLMixin):
    """Test Suites of my matches view"""
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                ]

    @classmethod
    def setUpTestData(cls):
        cls.organiser = User.objects.get(email='johndoe@example.org')
        cls.officer = User.objects.get(email='janedoe@example.org')
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.club = Club.objects.get(name="Test_Club")
        cls.group_tester = ClubGroupTester(cls.club)
        cls.tournament_tester = TournamentGroupTester(cls.tournament)
        cls.group_tester.make_officer(cls.officer)
        cls.url = reverse('add_co_organiser', kwargs={'club_name':cls.club.name, 'tournament_name': cls.tournament.name, 'user_id': cls.officer.id})
        cls.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        cls.show_tournament_url = reverse('show_tournament', kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})

    def setUp(self):
        self.client.login(email=self.organiser.email, password='Password123')

    def test_add_co_organiser_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/add_co_organiser/{self.officer.id}')

    def test_successful_add_co_organiser(self):
        notifications = len(self.officer.notifications.unread())
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        self.assertTrue(self.tournament.user_status(self.officer), "co_organiser")
        last_notification = self.officer.notifications.unread()[0].description
        self.assertEqual(len(self.officer.notifications.unread()), notifications + 1)
        self.assertEqual(last_notification, f"You have been assigned as co-organiser of tournament {self.tournament.name}")

    def test_add_co_organiser_with_wrong_id(self):
        bad_url = reverse('add_co_organiser', kwargs={'club_name':self.club.name, 'tournament_name': self.tournament.name, 'user_id': 9999})
        response = self.client.get(bad_url, follow=True)
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The officer you are looking for doesn't exist")

    def test_member_cannot_be_added_as_co_organiser(self):
        self.group_tester.make_member(self.officer)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_owner_cannot_be_added_as_co_organiser(self):
        url = reverse('add_co_organiser', kwargs={'club_name':self.club.name, 'tournament_name': self.tournament.name, 'user_id': self.organiser.id})
        response = self.client.get(url, follow=True)
        self._assert_response_redirect(response)

    def test_applicant_cannot_be_added_as_co_organiser(self):
        self.group_tester.make_applicant(self.officer)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_accepted_applicant_cannot_be_added_as_co_organiser(self):
        self.group_tester.make_accepted_applicant(self.officer)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_denied_applicant_cannot_be_added_as_co_organiser(self):
        self.group_tester.make_denied_applicant(self.officer)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_logged_in_non_members_cannot_be_added_as_co_organiser(self):
        self.group_tester.make_authenticated_non_member(self.officer)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('add_co_organiser', kwargs={'club_name':self.club.name, 'tournament_name': self.tournament.name, 'user_id': self.officer.id}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_add_co_organiser_in_wrong_tournament(self):
        bad_url = reverse('add_co_organiser', kwargs={'club_name': self.club.name, 'tournament_name': "oops", 'user_id': self.officer.id})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('show_club', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The tournament you are looking for does not exist!")

    def test_wrong_club_add_co_organiser(self):
        bad_url = reverse('add_co_organiser', kwargs={'club_name': "blabla", 'tournament_name': self.tournament.name,'user_id': self.officer.id})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def _assert_response_redirect(self, response):
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_valid_response(self, response):
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)





