from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, Tournament, Match, Player
from chessclubs.tests.helpers import ClubGroupTester


class MatchModelTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/default_player.json',
                'chessclubs/tests/fixtures/other_players.json',
                'chessclubs/tests/fixtures/default_match.json',
                ]

    def setUp(self):
        self.organiser = User.objects.get(email='johndoe@example.org')
        self.player1 = Player.objects.get(pk=1)
        self.player2 = Player.objects.get(pk=2)
        self.other_player = Player.objects.get(pk=3)
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

    def test_enter_winner_while_closed(self):
        self.match.enter_winner(self.player1)
        with self.assertRaises(ValidationError):
            new_winner = self.match.enter_winner(self.player2)
            self.assertEqual(new_winner, None)
            self.assertEqual(self.match.get_winner(), self.player1)

    def test_enter_winner_with_wrong_player(self):
        with self.assertRaises(ValueError):
            winner = self.match.enter_winner(self.other_player)
            self.assertEqual(winner, None)
            self.assertEqual(self.match.get_winner(), None)

    def test_successful_enter_draw(self):
        self.match.enter_draw()
        self.assertFalse(self.match.is_open())
        self.assertEqual(self.match.get_winner(), None)

    def test_enter_draw_while_closed(self):
        self.match.enter_draw()
        with self.assertRaises(ValidationError):
            self.match.enter_draw()

    def test_forbidden_return_winner(self):
        with self.assertRaises(ValidationError):
            winner = self.match.return_winner()
            self.assertEqual(winner, None)

    def test_successful_return_winner(self):
        self.match.enter_winner(self.player1)
        winner = self.match.return_winner()
        self.assertEqual(self.player1.user.full_name(), winner)


    def _assert_match_is_valid(self):
        try:
            self.match.full_clean()
        except ValidationError:
            self.fail('Test match should be valid')

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.match.full_clean()
