"""Unit tests for the Elimination rounds model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import Tournament, Club, SmallPoolPhase
from chessclubs.tests.helpers import generate_pools_list, get_right_number_of_pools

class SmallPoolPhaseModelTestCase(TestCase):
    """Unit tests for the tournament model at creation time."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/default_tournament.json',
        'chessclubs/tests/fixtures/other_small_pool_phase.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.MIN = 17
        self.MAX = 32
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.club = Club.objects.get(name="Test_Club")
        self.small_pool_phase = SmallPoolPhase.objects.get(pk=2)
        self.right_answers = get_right_number_of_pools()

    def test_generate_accurate_schedule(self):
        for i in range(self.MIN, self.MAX + 1):
            pools_list = generate_pools_list(i, self.club, self.tournament, self.small_pool_phase)
            self.assertEqual(len(pools_list), self.right_answers[i])
            self._clean()

    def test_no_player_is_in_more_than_1_pool(self):
        for i in range(self.MIN, self.MAX + 1):
            pools_list = generate_pools_list(i, self.club, self.tournament, self.small_pool_phase)
            for pool in pools_list:
                for other_pool in pools_list:
                    if other_pool != pool:
                        for player in other_pool.get_players():
                            self.assertTrue(player not in pool.get_players())
            self._clean()

    def _assert_round_is_valid(self):
        try:
            self.tournament.full_clean()
        except ValidationError:
            self.fail('Test tournament should be valid')

    def _assert_round_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()

    def _clean(self):
        for player in self.small_pool_phase.get_players():
            player.user.delete()
        self.small_pool_phase.pools_schedule.all().delete()
