
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, Tournament, Player, SmallPoolMatch
from chessclubs.tests.helpers import ClubGroupTester


class SmallPoolMatchModelTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/default_player.json',
                'chessclubs/tests/fixtures/other_players.json',
                'chessclubs/tests/fixtures/default_small_pool_phase.json',
                'chessclubs/tests/fixtures/default_small_pool.json',
                'chessclubs/tests/fixtures/default_match.json',
                'chessclubs/tests/fixtures/default_small_pool_match.json',
                ]

    def setUp(self):
        self.organiser = User.objects.get(email='johndoe@example.org')
        self.player1 = Player.objects.get(pk=1)
        self.player2 = Player.objects.get(pk=2)
        self.other_player = Player.objects.get(pk=3)
        self.club = Club.objects.get(name="Test_Club")
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_members([self.player1.user, self.player2.user])
        self.small_pool_match = SmallPoolMatch.objects.get(pk=1)

    def test_cannot_create_match_with_same_players(self):
        with self.assertRaises(ValueError):
            SmallPoolMatch.objects.create_match(tournament=self.tournament, player1=self.player1, player2=self.player1)

    def test_cannot_create_match_with_organiser(self):
        with self.assertRaises(ValueError):
            SmallPoolMatch.objects.create_match(tournament=self.tournament, player1=self.tournament.organiser,
                                                  player2=self.player1)

    def test_enter_result_while_closed(self):
        self.small_pool_match.enter_result(True, winner=self.player1)
        with self.assertRaises(ValidationError):
            self.small_pool_match.enter_result(True, winner=self.player2)
            self.assertFalse(self.small_pool_match.is_open())
            self.assertEqual(self.small_pool_match.get_winner(), None)

        with self.assertRaises(ValidationError):
            self.small_pool_match.enter_result(False)
            self.assertTrue(self.small_pool_match.is_open())
            self.assertEqual(self.small_pool_match.get_winner(), None)

    def test_enter_result_with_non_player(self):
        with self.assertRaises(ValueError):
            self.small_pool_match.enter_result(True, winner=self.other_player)
            self.assertTrue(self.small_pool_match.is_open())
            self.assertEqual(self.small_pool_match.get_winner(), None)

    def test_successful_enter_winner_result(self):
        before_points = self.player1.get_points()
        self.small_pool_match.enter_result(True, winner=self.player1)
        self.player1.refresh_from_db()
        self.assertFalse(self.small_pool_match.is_open())
        winner = self.small_pool_match.get_winner()
        after_points = self.player1.get_points()
        self.assertEqual(winner, self.player1)
        self.assertEqual(winner.get_points(), self.player1.get_points())
        self.assertEqual(before_points + 1, after_points)
        if self.small_pool_match.get_player1() == self.player1:
            self.assertEqual(self.small_pool_match.get_player1().get_points(), after_points)
        else:
            self.assertEqual(self.small_pool_match.get_player2().get_points(), after_points)

    def test_successful_enter_draw_result(self):
        before_points1 = self.player1.get_points()
        before_points2 = self.player2.get_points()
        self.small_pool_match.enter_result(False)
        self.player1.refresh_from_db()
        self.player2.refresh_from_db()
        self.assertFalse(self.small_pool_match.is_open())
        winner = self.small_pool_match.get_winner()
        after_points1 = self.player1.get_points()
        after_points2 = self.player1.get_points()
        self.assertEqual(winner, None)
        self.assertEqual(before_points1 + 0.5, after_points1)
        self.assertEqual(before_points2 + 0.5, after_points2)
        if self.small_pool_match.get_player1() == self.player1:
            self.assertEqual(self.small_pool_match.get_player1().get_points(), after_points1)
            self.assertEqual(self.small_pool_match.get_player2().get_points(), after_points2)
        else:
            self.assertEqual(self.small_pool_match.get_player2().get_points(), after_points1)
            self.assertEqual(self.small_pool_match.get_player1().get_points(), after_points2)

    def _assert_match_is_valid(self):
        try:
            self.small_pool_match.full_clean()
        except ValidationError:
            self.fail('Test elimination match should be valid')

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.small_pool_match.full_clean()

