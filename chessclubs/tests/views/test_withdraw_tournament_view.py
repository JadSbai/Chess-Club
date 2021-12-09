"""Tests of the withdraw from the tournament view."""
from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club, Tournament
from django.contrib import messages
from chessclubs.tests.helpers import ClubGroupTester, TournamentGroupTester, reverse_with_next
from django.core.exceptions import ObjectDoesNotExist
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN

class WithdrawTournamentTestCase(TestCase):
    """Tests of the withdraw from the tournament view."""

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                ]

    def setUp(self):
        self.club = Club.objects.get(name="Test_Club") # club
        self.club_owner = User.objects.get(email='johndoe@example.org') # clubs owner john doe
        self.user = User.objects.get(email='janedoe@example.org') # get a jane member and make it a club member
        self.group_tester = ClubGroupTester(self.club)
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.tournament_tester = TournamentGroupTester(self.tournament)

        self.client.login(email=self.user.email, password='Password123')

        self.url = reverse('withdraw_tournament', kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name})
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_withdraw_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/withdraw/')

    def test_club_members_can_withdraw_from_tournament(self):
        self.group_tester.make_member(self.user)
        self.tournament_tester.make_participant(self.user)
        self.client.get(self.url, follow=True)
        self.assertFalse(self.tournament.is_participant(self.user))

    def test_club_officers_can_withdraw_from_tournament(self):
        self.group_tester.make_officer(self.user)
        self.tournament_tester.make_participant(self.user)
        self.client.get(self.url, follow=True)
        self.assertFalse(self.tournament.is_participant(self.user))

    def test_club_owner_can_withdraw_from_tournament(self):
        self.tournament_tester.make_participant(self.club_owner)
        self.client.get(self.url, follow=True)
        self.assertFalse(self.tournament.is_participant(self.club_owner))

    # TODO:
    # Organiser cannot withdraw from tournament
    # Co-organiser cannot withdraw from tournament
    # Non club members - applicants, denied applicants, accepted applicants, authenticated non members - cannot withdraw from tournament
    # No withdrawals after deadline
    # Can withdraw before the deadline

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('withdraw_tournament',
                                                           kwargs={'club_name': self.club.name,
                                                                   'tournament_name': self.tournament.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)