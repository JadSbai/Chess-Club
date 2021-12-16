"""Unit tests for the tournament model at creation time."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import Tournament, Player, Club
from django.utils import timezone
from chessclubs.tests.helpers import _create_test_players, enter_results_to_all_matches


class TournamentModelTestCase(TestCase):
    """Unit tests for the tournament model at creation time."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_players.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/other_clubs.json',
        'chessclubs/tests/fixtures/default_tournament.json',
        'chessclubs/tests/fixtures/other_tournaments.json',
        'chessclubs/tests/fixtures/empty_tournament.json',
    ]

    @classmethod
    def setUpTestData(cls):
        cls.MAX = 96
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.second_tournament = Tournament.objects.get(name="Test_Tournament2")
        cls.new_tournament = Tournament.objects.get(name="Empty_Tournament")
        cls.new_tournament._set_deadline_now()
        cls.club = Club.objects.get(name="Test_Club")
        cls.player = Player.objects.get(pk=1)
        cls.player_list = _create_test_players(cls.MAX, cls.club, cls.new_tournament)

    def tearDown(self):
        self.new_tournament.pool_phases.all().delete()

    def test_organiser_must_not_be_blank(self):
        self.tournament.organiser = None
        self._assert_tournament_is_invalid()

    def test_name_must_not_be_blank(self):
        self.tournament.name = ''
        self._assert_tournament_is_invalid()

    def test_name_must_be_unique(self):
        self.tournament.name = self.second_tournament.name
        self._assert_tournament_is_invalid()

    def test_location_must_not_be_blank(self):
        self.tournament.location = ''
        self._assert_tournament_is_invalid()

    def test_name_may_contain_50_characters(self):
        self.tournament.name = 'x' * 50
        self._assert_tournament_is_valid()

    def test_name_must_not_contain_more_than_50_characters(self):
        self.tournament.name = 'x' * 51
        self._assert_tournament_is_invalid()

    def test_location_may_contain_50_characters(self):
        self.tournament.location = 'x' * 50
        self._assert_tournament_is_valid()

    def test_location_must_not_contain_more_than_50_characters(self):
        self.tournament.location = 'x' * 51
        self._assert_tournament_is_invalid()

    def test_location_need_not_be_unique(self):
        self.tournament.location = self.second_tournament.location
        self._assert_tournament_is_valid()

    def test_capacity_cannot_be_more_than_MAX_CAPACITY(self):
        self.tournament.max_capacity = 97
        self._assert_tournament_is_invalid()

    def test_capacity_cannot_be_less_than_MIN_CAPACITY(self):
        self.tournament.max_capacity = 1
        self._assert_tournament_is_invalid()

    def test_deadline_must_be_after_creation_date(self):
        self.tournament.deadline = timezone.now()
        self._assert_tournament_is_invalid()

    def test_deadline_cannot_be_blank(self):
        self.tournament.deadline = ""
        self._assert_tournament_is_invalid()

    def test_winner_may_be_blank(self):
        self.tournament._winner = None
        self._assert_tournament_is_valid()

    def test_description_cannot_be_blank(self):
        self.tournament.description = ""
        self._assert_tournament_is_invalid()

    def test_phase_transitions(self):
        self.new_tournament.start_tournament()
        self.assertTrue(self.new_tournament.is_published())
        self.assertTrue(self.new_tournament.has_started())
        large_pool_phase = self.new_tournament.get_current_pool_phase()
        self.assertFalse(large_pool_phase is None)
        self.assertEqual(large_pool_phase.get_players_count(), self.MAX)
        self.assertEqual(len(self.new_tournament.get_current_schedule()), len(large_pool_phase.get_all_matches()))
        enter_results_to_all_matches(self.new_tournament)
        self.assertEqual(len(large_pool_phase.get_all_matches()), 0)
        small_pool_phase = self.new_tournament.get_current_pool_phase()
        self.assertFalse(small_pool_phase is None)
        self.assertEqual(small_pool_phase.get_players_count(), 32)
        for pool in small_pool_phase.get_pools():
            self.assertEqual(pool.get_players_count(), 4)
        enter_results_to_all_matches(self.new_tournament)
        self.assertEqual(len(small_pool_phase.get_all_matches()), 0)
        elimination_round = self.new_tournament.elimination_round
        self.assertFalse(elimination_round is None)
        self.assertEqual(elimination_round.get_players_count(), 16)
        self.assertEqual(len(self.new_tournament.get_current_schedule()), elimination_round.schedule.count())
        self.assertEqual(elimination_round.phase, "Eighth-Final")
        enter_results_to_all_matches(self.new_tournament)
        elimination_round.refresh_from_db()
        self.assertEqual(elimination_round.phase, "Quarter-Final")
        enter_results_to_all_matches(self.new_tournament)
        elimination_round.refresh_from_db()
        self.assertEqual(elimination_round.phase, "Semi-Final")
        enter_results_to_all_matches(self.new_tournament)
        elimination_round.refresh_from_db()
        self.assertEqual(elimination_round.phase, "Final")
        enter_results_to_all_matches(self.new_tournament)
        self.new_tournament.refresh_from_db()
        self.assertTrue(self.new_tournament._started)
        self.assertTrue(self.new_tournament._finished)
        self.assertFalse(self.new_tournament.get_winner() is None)

    def test_get_current_schedule_is_accurate(self):
        self.new_tournament.start_tournament()
        before = len(self.new_tournament.get_current_schedule())
        pool = self.new_tournament.get_current_pool_phase().get_pools()[0]
        pool_match = pool.get_pool_matches()[0]
        pool.enter_result(match=pool_match, result=True, winner=pool_match.get_player1())
        after = len(self.new_tournament.get_current_schedule())
        self.assertEqual(before, after + 1)

    def test_get_current_pool_phase(self):
        self.new_tournament.start_tournament()
        self.assertFalse(self.new_tournament.get_current_pool_phase() is None)

    def test_enter_results_to_all_matches(self):
        self.new_tournament.start_tournament()
        while not self.new_tournament.has_finished():
            enter_results_to_all_matches(self.new_tournament)
            self.new_tournament.refresh_from_db()
        self.assertTrue(self.new_tournament.has_finished())

    def _assert_tournament_is_valid(self):
        try:
            self.tournament.full_clean()
        except ValidationError:
            self.fail('Test tournament should be valid')

    def _assert_tournament_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()
