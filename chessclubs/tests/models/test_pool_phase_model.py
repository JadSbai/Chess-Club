"""Unit tests for the Elimination rounds model."""
import random

from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import Tournament, Club, PoolPhase
from chessclubs.tests.helpers import generate_pools_list, get_right_number_of_pools, _create_test_players, remove_all_players

class SmallPoolPhaseModelTestCase(TestCase):
    """Unit tests for the tournament model at creation time."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/default_tournament.json',
        'chessclubs/tests/fixtures/small_pool_phase.json',
        'chessclubs/tests/fixtures/large_pool_phase.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.MIN = 17
        self.MID = 33
        self.MAX = 96
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.club = Club.objects.get(name="Test_Club")
        self.small_pool_phase = PoolPhase.objects.get(pk=1)
        self.large_pool_phase = PoolPhase.objects.get(pk=2)
        self.right_answers = get_right_number_of_pools()
        self.list_of_players = _create_test_players(self.MAX, self.club, self.tournament)

    def test_generate_accurate_schedule_for_small_size(self):
        for i in range(self.MIN, self.MID):
            players = random.sample(self.list_of_players, i)
            pools_list = generate_pools_list(players, self.small_pool_phase)
            self.assertEqual(len(pools_list), self.right_answers[i])
            self._clean(self.small_pool_phase)

    def test_generate_accurate_schedule_for_large_size(self):
        for i in range(self.MID, self.MAX + 1):
            players = random.sample(self.list_of_players, i)
            pools_list = generate_pools_list(players, self.large_pool_phase)
            self.assertTrue(9 <= len(pools_list) <= 16)
            self._clean(self.large_pool_phase)

    def test_no_player_is_in_more_than_1_pool(self):
        for i in range(self.MIN, self.MAX + 1):
            players = random.sample(self.list_of_players, i)
            pools_list = generate_pools_list(players, self.small_pool_phase)
            for pool in pools_list:
                for other_pool in pools_list:
                    if other_pool != pool:
                        for player in other_pool.get_players():
                            self.assertTrue(player not in pool.get_players())
            self._clean(self.small_pool_phase)

    def test_name_must_be_unique(self):
        self.large_pool_phase.name = "Small-Pool-Phase"
        self._assert_phase_is_invalid(self.large_pool_phase)

    def test_name_must_be_among_choices(self):
        self.large_pool_phase.name = "bad choice"
        self._assert_phase_is_invalid(self.large_pool_phase)

    def test_name_cannot_be_blank(self):
        self.large_pool_phase.name = ""
        self._assert_phase_is_invalid(self.large_pool_phase)

    def test_unique_combination(self):
        self.large_pool_phase.name = self.small_pool_phase.name
        self._assert_phase_is_invalid(self.large_pool_phase)

    def _assert_phase_is_valid(self, phase):
        try:
            phase.full_clean()
        except ValidationError:
            self.fail('Test tournament should be valid')

    def _assert_phase_is_invalid(self, phase):
        with self.assertRaises(ValidationError):
            phase.full_clean()

    def _clean(self, phase):
        remove_all_players(phase)
        phase.pools.all().delete()