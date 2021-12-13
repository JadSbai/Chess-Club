import math
import random

from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, Tournament, EliminationRounds
from chessclubs.tests.helpers import ClubGroupTester, generate_elimination_matches_schedule, get_right_phase, \
    _create_test_players, enter_results_to_elimination_round_matches


class EliminationRoundTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/default_elimination_round.json',
                ]

    def setUp(self):
        self.MIN = 2
        self.MAX = 17
        self.user = User.objects.get(email='johndoe@example.org')
        self.other_user = User.objects.get(email="janedoe@example.org")
        self.club = Club.objects.get(name="Test_Club")
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.elimination_round = EliminationRounds.objects.get(pk=1)
        self.group_tester = ClubGroupTester(self.club)
        self.right_phases = get_right_phase()
        self.players_list = _create_test_players(self.MAX, self.club, self.tournament)

    def test_get_accurate_matches_schedule(self):
        for count in range(2, 17):
            players = random.sample(self.players_list, count)
            schedule = generate_elimination_matches_schedule(players, self.elimination_round)
            number_of_matches = self.elimination_round.schedule.all().count()
            self.assertEqual(number_of_matches, len(schedule))
            self.assertEqual(number_of_matches, math.floor(count / 2))
            self._assert_elimination_round_is_valid()
            self._clean()

    def test_phase_transition(self):
        players = random.sample(self.players_list, 16)
        generate_elimination_matches_schedule(players, self.elimination_round)
        self.assertEqual(self.elimination_round.phase, "Eighth-Final")
        enter_results_to_elimination_round_matches(self.elimination_round)
        self.assertEqual(self.elimination_round.phase, "Quarter-Final")
        enter_results_to_elimination_round_matches(self.elimination_round)
        self.assertEqual(self.elimination_round.phase, "Semi-Final")
        enter_results_to_elimination_round_matches(self.elimination_round)
        self.assertEqual(self.elimination_round.phase, "Final")
        enter_results_to_elimination_round_matches(self.elimination_round)
        self.assertFalse(self.elimination_round._open)

    def test_phase_must_be_among_choices(self):
        self.elimination_round.phase = "bad_choice"
        self._assert_elimination_round_is_invalid()

    def test_phase_cannot_be_blank(self):
        self.elimination_round.phase = ''
        self._assert_elimination_round_is_invalid()

    def test_set_phase_is_accurate(self):
        for count in range(2, 17):
            players = random.sample(self.players_list, count)
            generate_elimination_matches_schedule(players, self.elimination_round)
            self.assertEqual(self.right_phases[count], self.elimination_round.phase)
            self._clean()

    def _assert_elimination_round_is_valid(self):
        try:
            self.elimination_round.full_clean()
        except ValidationError:
            self.fail('Test elimination round should be valid')

    def _assert_elimination_round_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.elimination_round.full_clean()

    def _clean(self):
        for player in self.elimination_round.get_players():
            self.elimination_round.remove_player(player)
        self.elimination_round.clean_schedule()
