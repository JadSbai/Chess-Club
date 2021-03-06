"""Tests of my matches view"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next, TournamentGroupTester, _create_test_players, \
    enter_results_to_all_matches
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages
from with_asserts.mixin import AssertHTMLMixin


class MyMatchesViewTestCase(TestCase, AssertHTMLMixin):
    """Test Suites of my matches view"""
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                ]

    @classmethod
    def setUpTestData(cls):
        cls.participant = User.objects.get(email='janedoe@example.org')
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.club = Club.objects.get(name="Test_Club")
        cls.group_tester = ClubGroupTester(cls.club)
        cls.tournament_tester = TournamentGroupTester(cls.tournament)
        cls.group_tester.make_member(cls.participant)
        cls.url = reverse('my_matches')
        cls.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        _create_test_players(3, cls.club, cls.tournament)

    def setUp(self):
        self.client.login(email=self.participant.email, password='Password123')

    def test_my_applications_url(self):
        self.assertEqual(self.url, f'/my_matches/')

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('my_matches'))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_no_matches(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_matches.html")
        with self.assertHTML(response) as html:
            no_match = html.find('.//i[@id="no_matches"]')
            self.assertIsNotNone(no_match)
            self.assertEqual(no_match.text, "You are currently not playing in any tournament.")

    def test_matches_in_unpublished_tournament(self):
        self.tournament_tester.make_participant(self.participant)
        self.tournament._set_deadline_now()
        response = self.client.get(self.url)
        with self.assertHTML(response, element_id="not_published") as no_match_left:
            self.assertIsNotNone(no_match_left)
            self.assertEqual(no_match_left.text, "The schedule has not been published yet.")

    def test_matches_in_no_matches_currently_left_to_play_tournament(self):
        self.tournament_tester.make_participant(self.participant)
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        my_matches = self.tournament.get_matches_of_player(self.participant)
        for match in my_matches:
            match.enter_winner(match.get_player1())
        response = self.client.get(self.url)
        with self.assertHTML(response, element_id="no_match_to_play_in_tournament") as no_match:
            self.assertIsNotNone(no_match)
            self.assertEqual(no_match.text, "You have no more matches in this tournament for now.")

    def test_matches_in_published_tournament(self):
        self.tournament_tester.make_participant(self.participant)
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        response = self.client.get(self.url)
        with self.assertHTML(response, '.matches') as matches:
            self.assertEqual(len(matches), 1)
            for match in matches:
                text = match.find('.//p').text
                self.assertTrue("You" in text)





