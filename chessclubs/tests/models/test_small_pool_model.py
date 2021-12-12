from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.test import TestCase
from chessclubs.models import User, Club, Tournament, Player, Pool, PoolMatch
from chessclubs.tests.helpers import ClubGroupTester


class SmallPoolModelTestCase(TestCase):
    """Test Suites for the Small Pool model"""
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/default_player.json',
                'chessclubs/tests/fixtures/other_players.json',
                'chessclubs/tests/fixtures/default_elimination_round.json',
                'chessclubs/tests/fixtures/default_small_pool_phase.json',
                'chessclubs/tests/fixtures/default_small_pool.json',
                ]

    def setUp(self):
        self.organiser = User.objects.get(email='johndoe@example.org')
        self.player1 = Player.objects.get(pk=1)
        self.player2 = Player.objects.get(pk=2)
        self.player3 = Player.objects.get(pk=3)
        self.player4 = Player.objects.get(pk=4)
        self.club = Club.objects.get(name="Test_Club")
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_members([self.player1.user, self.player2.user, self.player3.user, self.player4.user])
        self.small_pool = Pool.objects.get(pk=1)
        self.small_pool.create_matches()

    def test_create_matches(self):
        num = self.small_pool.get_players_count()
        pool_matches = self.small_pool.pool_matches.all()
        self.assertEqual(pool_matches.count(), (num * (num - 1)) / 2)
        for player in self.small_pool.get_players():
            for other_player in self.small_pool.get_players():
                if player != other_player:
                    count = 0
                    for match in self.small_pool.pool_matches.all():
                        if (match.get_player1() == player and match.get_player2() == other_player) or (
                                match.get_player1() == other_player and match.get_player2() == player):
                            count += 1
                    self.assertEqual(count, 1)

    def test_enter_all_results(self):
        players = self.small_pool.get_players()
        match1 = self._get_match(self.player1, self.player2)
        self.small_pool.enter_result(match1, True, self.player1)

        match2 = self._get_match(self.player3, self.player1)
        self.small_pool.enter_result(match2, True, self.player3)

        match3 = self._get_match(self.player1, self.player4)
        self.small_pool.enter_result(match3, True, self.player1)

        match4 = self._get_match(self.player2, self.player3)
        self.small_pool.enter_result(match4, False)

        match5 = self._get_match(self.player2, self.player4)
        self.small_pool.enter_result(match5, True, self.player2)

        match6 = self._get_match(self.player3, self.player4)
        self.small_pool.enter_result(match6, True, self.player3)

        self.player1.refresh_from_db()
        self.player2.refresh_from_db()
        self.player3.refresh_from_db()
        self.player4.refresh_from_db()

        self.assertEqual(players[0], self.player3)
        self.assertEqual(players[1], self.player1)
        self.assertEqual(players[2], self.player2)
        self.assertEqual(players[3], self.player4)

        self.assertEqual(self.player3.get_points(), 2.5)
        self.assertEqual(self.player1.get_points(), 2.0)
        self.assertEqual(self.player2.get_points(), 1.5)
        self.assertEqual(self.player4.get_points(), 0.0)

        self.assertTrue(self.small_pool.all_matches_played)

    def _get_match(self, player1, player2):
        try:
            match = PoolMatch.objects.get(_player1=player1, _player2=player2)
            return match
        except ObjectDoesNotExist:
            return PoolMatch.objects.get(_player1=player2, _player2=player1)

    def _assert_match_is_valid(self):
        try:
            self.small_pool.full_clean()
        except ValidationError:
            self.fail('Test elimination match should be valid')

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.small_pool.full_clean()
