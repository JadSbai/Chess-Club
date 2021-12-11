"""Tests of the withdraw from the tournament view."""
from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, TournamentGroupTester, reverse_with_next
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN

class WithdrawTournamentTestCase(TestCase):
    """Tests of the withdraw from the tournament view."""

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                ]

    def setUp(self):
        self.club = Club.objects.get(name="Test_Club")
        self.user = User.objects.get(email='janedoe@example.org')
        self.group_tester = ClubGroupTester(self.club)
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.tournament_tester = TournamentGroupTester(self.tournament)
        self.client.login(email=self.user.email, password='Password123')
        self.url = reverse('withdraw_tournament', kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name})
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_withdraw_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/withdraw/')

    def test_club_member_participant_can_withdraw_from_tournament(self):
        # self.group_tester.make_member(self.user)
        # self.tournament_tester.make_participant(self.user)
        # print(self.user.first_name, self.tournament.is_participant(self.user))
        # self.client.get(self.url, follow=True)
        # self.assertFalse(self.tournament.is_participant(self.user))
        pass

    def test_club_officer_participant_can_withdraw_from_tournament(self):
        # self.group_tester.make_officer(self.user)
        # self.tournament_tester.make_participant(self.user)
        # print(self.user.first_name, self.tournament.is_participant(self.user))
        # self.client.get(self.url, follow=True)
        # self.assertFalse(self.tournament.is_participant(self.user))
        pass

    def test_club_owner_participant_can_withdraw_from_tournament(self):
        pass

    def test_tournament_co_organisers_can_withdraw(self):
        pass

    def test_tournament_organiser_cannot_withdraw(self):
        pass

    def test_non_club_members_cannot_withdraw(self):
        pass

    def test_non_participants_cannot_withdraw(self):
        pass

    def test_can_withdraw_before_deadline(self):
        pass

    def test_cannot_withdraw_after_deadline(self):
        pass

    def can_withdraw_regardless_of_capacity(self):
        pass

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('withdraw_tournament',
                                                           kwargs={'club_name': self.club.name,
                                                                   'tournament_name': self.tournament.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
