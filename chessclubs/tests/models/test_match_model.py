from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, Tournament, Match, Player
from chessclubs.tests.helpers import ClubGroupTester


class MatchModelTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/default_players.json',
                'chessclubs/tests/fixtures/default_match.json',
                ]

    def setUp(self):
        self.organiser = User.objects.get(email='johndoe@example.org')
        self.player1 = Player.objects.get(pk=8)
        self.player2 = Player.objects.get(pk=9)
        self.other_player = Player.objects.get(pk=1)
        self.club = Club.objects.get(name="Test_Club")
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_member(self.player1.user)
        self.group_tester.make_member(self.player2.user)
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

    def test_successful_enter_winner(self):
        winner = self.match.enter_winner(self.player1)
        self.assertEqual(winner, self.player1)
        self.assertEqual(self.match.get_winner(), self.player1)
        self.assertFalse(self.match.is_open())

    def test_successful_enter_draw(self):
        self.match.enter_draw()
        self.assertFalse(self.match.is_open())
        self.assertEqual(self.match.get_winner(), None)

    def test_forbidden_get_winner(self):
        winner = self.match.get_winner()
        self.assertEqual(winner, None)

    def test_successful_get_winner(self):
        self.match.enter_winner(self.player1)
        winner = self.match.get_winner()
        self.assertEqual(self.player1, winner)

    def test_player1_and_player2_have_encountered_each_other(self):
        self.match.enter_winner(self.player1)
        self.assertTrue(self.player2 in self.player1.get_encountered_players())
        self.assertTrue(self.player1 in self.player2.get_encountered_players())

    def _assert_match_is_valid(self):
        try:
            self.match.full_clean()
        except ValidationError:
            self.fail('Test match should be valid')

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.match.full_clean()
