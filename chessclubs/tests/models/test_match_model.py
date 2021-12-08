from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, Tournament, Match
from chessclubs.tests.helpers import ClubGroupTester


class MatchModelTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/default_match.json',
                ]

    def setUp(self):
        self.organiser = User.objects.get(email='johndoe@example.org')
        self.player1 = User.objects.get(email="janedoe@example.org")
        self.player2 = User.objects.get(email="petrapickles@example.org")
        self.club = Club.objects.get(name="Test_Club")
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_member(self.player1)
        self.group_tester.make_member(self.player2)
        self.tournament.add_participant(self.player1)
        self.tournament.add_participant(self.player2)
        self.match = Match.objects.get(pk=1)

    def test_cannot_create_match_with_same_players(self):
        with self.assertRaises(ValueError):
            Match.objects.create_match(tournament=self.tournament, player1=self.player1, player2=self.player1)

    def test_cannot_create_match_with_organiser(self):
        with self.assertRaises(ValueError):
            Match.objects.create_match(tournament=self.tournament, player1=self.tournament.organiser,
                                               player2=self.player1)

    def test_winner_can_be_null(self):
        self.match.winner = None
        self._assert_match_is_valid()

    def test_players_cannot_be_null(self):
        self.match._player1_id = 9999
        self._assert_match_is_invalid()
        self.match._player2_id = 9999
        self._assert_match_is_invalid()

    def _assert_match_is_valid(self):
        try:
            self.match.full_clean()
        except ValidationError:
            self.fail('Test match should be valid')

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.match.full_clean()
