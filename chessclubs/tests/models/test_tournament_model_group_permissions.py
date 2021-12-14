"""Unit tests for the tournament model permissions."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import TournamentGroupTester


class TournamentGroupPermissionsTestCase(TestCase):
    """Unit tests for the Tournament Group permissions. Assess that groups in tournaments possess the appropriate permissions"""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/default_tournament.json',
    ]

    @classmethod
    def setUpTestData(cls):
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.organiser = cls.tournament.organiser
        cls.co_organiser = User.objects.get(email="petrapickles@example.org")
        cls.player = User.objects.get(email='janedoe@example.org')
        cls.group_tester = TournamentGroupTester(cls.tournament)
        cls.group_tester.make_participant(cls.player)
        cls.group_tester.make_co_organiser(cls.co_organiser)

    def test_participant_can_play_matches(self):
        if not self.player.has_tournament_perm('chessclubs.play_matches', self.tournament):
            self.fail('Participant should be allowed to play matches')

    def test_participant_cannot_enter_match_results(self):
        if self.player.has_tournament_perm('chessclubs.enter_match_results', self.tournament):
            self.fail('Participant should not be allowed to enter match results')

    def test_participant_can_see_tournament_private_info(self):
        if not self.player.has_tournament_perm('chessclubs.see_tournament_private_info', self.tournament):
            self.fail('Participant should be allowed to see tournament private info')

    def test_participant_can_withdraw(self):
        if not self.player.has_tournament_perm('chessclubs.withdraw', self.tournament):
            self.fail('Participant should be able to withdraw')

    def test_organiser_cannot_play_matches(self):
        if self.organiser.has_tournament_perm('chessclubs.play_matches', self.tournament):
            self.fail('Organiser should not be allowed to play matches')

    def test_organiser_can_enter_match_results(self):
        if not self.organiser.has_tournament_perm('chessclubs.enter_match_results', self.tournament):
            self.fail('Organiser should be allowed to enter match results')

    def test_organiser_can_see_tournament_private_info(self):
        if not self.organiser.has_tournament_perm('chessclubs.see_tournament_private_info', self.tournament):
            self.fail('Organiser should be allowed to see tournament private info')

    def test_organiser_cannot_withdraw(self):
        if self.organiser.has_tournament_perm('chessclubs.withdraw', self.tournament):
            self.fail('Organiser should not be able to withdraw')

    def test_co_organiser_cannot_play_matches(self):
        if self.co_organiser.has_tournament_perm('chessclubs.play_matches', self.tournament):
            self.fail('Co_Organiser should not be allowed to play matches')

    def test_co_organiser_can_enter_match_results(self):
        if not self.co_organiser.has_tournament_perm('chessclubs.enter_match_results', self.tournament):
            self.fail('Co_Organiser should be allowed to enter match results')

    def test_co_organiser_can_see_tournament_private_info(self):
        if not self.co_organiser.has_tournament_perm('chessclubs.see_tournament_private_info', self.tournament):
            self.fail('Co_Organiser should be allowed to see tournament private info')

    def test_co_organiser_cannot_withdraw(self):
        if self.co_organiser.has_tournament_perm('chessclubs.withdraw', self.tournament):
            self.fail('Co-organiser should be able to withdraw')