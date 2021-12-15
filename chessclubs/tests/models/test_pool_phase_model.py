"""Unit tests for the Elimination rounds model."""
import random

from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import Tournament, Club, PoolPhase
from chessclubs.tests.helpers import generate_pools_list, get_right_number_of_pools, _create_test_players, \
    remove_all_players, encounter_all, encounter_half


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

    @classmethod
    def setUpTestData(cls):
        cls.MIN = 17
        cls.MID = 33
        cls.MAX = 96
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.club = Club.objects.get(name="Test_Club")
        cls.small_pool_phase = PoolPhase.objects.get(pk=1)
        cls.large_pool_phase = PoolPhase.objects.get(pk=2)
        cls.right_answers = get_right_number_of_pools()
        cls.list_of_players = _create_test_players(cls.MAX, cls.club, cls.tournament)

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

    def test_every_player_is_in_1_pool(self):
        for i in range(self.MIN, self.MAX + 1):
            players = random.sample(self.list_of_players, i)
            pools_list = generate_pools_list(players, self.small_pool_phase)
            counter = 0
            for player in self.small_pool_phase.get_players():
                for pool in pools_list:
                    if player in pool.get_players():
                        counter += 1
                self.assertEqual(counter, 1)
                counter = 0
            self._clean(self.small_pool_phase)

    def test_encounter_as_late_as_possible(self):
        for count in range(self.MIN, self.MAX + 1):
            players = random.sample(self.list_of_players, count)

            # Every player encounters exactly one player or no one
            encounter_half(players)
            pools_list = generate_pools_list(players, self.small_pool_phase)
            anomalies = 0
            for pool in pools_list:
                for player in pool.get_players():
                    for other_player in pool.get_players():
                        if other_player != player and (player in other_player.get_encountered_players()):
                            anomalies += 1
            self.assertTrue(anomalies <= 2 * len(pools_list))  # At MOST 1 pair of player have encountered each other in each pool
            self._clean(self.small_pool_phase)

            # Every player encounters every player
            encounter_all(players)
            pools_list = generate_pools_list(players, self.small_pool_phase)
            if 17 <= count <= 32:
                self.assertEqual(len(pools_list), self.right_answers[count])
            else:
                self.assertTrue(9 <= len(pools_list) <= 16)
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
        for player in phase.get_players():
            player._clean_encountered_players()
        remove_all_players(phase)
        phase.pools.all().delete()
