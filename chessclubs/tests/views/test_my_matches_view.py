"""Tests of my matches view"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next, TournamentGroupTester, _create_test_players
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
        _create_test_players(5, cls.club, cls.tournament)

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
            self.assertEqual(no_match.text, "You currently have no matches undergoing.")

    def test_matches_in_unpublished_tournament(self):
        self.tournament_tester.make_participant(self.participant)
        self.tournament._set_deadline_now()
        response = self.client.get(self.url)
        with self.assertHTML(response, element_id="not_published") as no_match:
            self.assertIsNotNone(no_match)
            self.assertEqual(no_match.text, "The schedule hasn't been published yet.")

    def test_matches_in_published_tournament(self):
        self.tournament_tester.make_participant(self.participant)
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        response = self.client.get(self.url)
        with self.assertHTML(response, '.matches') as no_match:
            self.assertIsNotNone(no_match)
            self.assertEqual(no_match.text, "The schedule hasn't been published yet.")



