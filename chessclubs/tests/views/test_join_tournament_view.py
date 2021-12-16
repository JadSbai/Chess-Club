"""Tests of apply to the tournament view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse

from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next, TournamentGroupTester, _create_test_players


class JoinTournamentViewTestCase(TestCase):
    """Tests of apply to the tournament view."""

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json'
                ]

    @classmethod
    def setUpTestData(cls):
        cls.club = Club.objects.get(name="Test_Club")
        cls.organiser = User.objects.get(email='johndoe@example.org')  # also tournament organiser
        cls.non_participant = User.objects.get(email='janedoe@example.org')
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.group_tester = ClubGroupTester(cls.club)
        cls.tournament_tester = TournamentGroupTester(cls.tournament)
        cls.url = reverse('join_tournament',
                          kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.show_tournament_url = reverse('show_tournament',
                                          kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.redirect_url = reverse('show_club', kwargs={'club_name': cls.club.name})

    def setUp(self):
        self.group_tester.make_member(self.non_participant)
        self.client.login(email=self.non_participant.email, password='Password123')

    def test_view_apply_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/join/')

    def test_successful_join(self):
        before = self.tournament.get_participant_count()
        response = self.client.get(self.url, follow=True)
        after = self.tournament.get_participant_count()
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        self.assertEqual(before + 1, after)
        self.assertTrue(self.tournament.is_participant(self.non_participant))

    def test_cannot_join_after_deadline(self):
        self.tournament._set_deadline_now()
        self._assert_invalid_join()

    def test_cannot_join_if_maximum_capacity_exceeded(self):
        _create_test_players(self.tournament.max_capacity, self.club, self.tournament)
        self._assert_invalid_join()

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('join_tournament', kwargs={'club_name': self.club.name,
                                                                                      'tournament_name': self.tournament.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_can_join(self):
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_officer_can_join(self):
        self.group_tester.make_officer(self.non_participant)
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_applicant_cannot_join(self):
        self.group_tester.make_applicant(self.non_participant)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response, self.redirect_url)

    def test_accepted_applicant_cannot_join(self):
        self.group_tester.make_accepted_applicant(self.non_participant)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response, self.redirect_url)

    def test_denied_applicant_cannot_join(self):
        self.group_tester.make_denied_applicant(self.non_participant)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response, self.redirect_url)

    def test_logged_in_non_members_cannot_join(self):
        self.group_tester.make_authenticated_non_member(self.non_participant)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response, self.redirect_url)

    def test_organiser_cannot_join(self):
        self.client.logout()
        self.client.login(email=self.organiser.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response, self.show_tournament_url)

    def test_co_organiser_cannot_join(self):
        self.tournament_tester.make_co_organiser(self.non_participant)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response, self.show_tournament_url)

    def test_participant_cannot_join(self):
        self.tournament_tester.make_participant(self.non_participant)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response, self.show_tournament_url)

    def test_non_participant_can_join(self):
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_join_wrong_tournament(self):
        bad_url = reverse('join_tournament', kwargs={'club_name': self.club.name, 'tournament_name': "oops"})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('show_club', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The tournament you are looking for does not exist!")

    def test_wrong_club_join_tournament(self):
        bad_url = reverse('join_tournament', kwargs={'club_name': "blabla", 'tournament_name': self.tournament.name})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def _assert_invalid_join(self):
        before = self.tournament.get_participant_count()
        response = self.client.get(self.url, follow=True)
        after = self.tournament.get_participant_count()
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        self.assertEqual(before, after)
        self.assertFalse(self.tournament.is_participant(self.non_participant))
        self.assertTrue(self.tournament.user_status(self.non_participant), "non_participant")
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_response_redirect(self, response, url):
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_valid_response(self, response):
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        for message in messages_list:
            self.assertNotEqual(message.level, messages.WARNING)
