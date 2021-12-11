"""Unit tests for the tournament model at creation time."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import Tournament
from django.utils import timezone

class TournamentModelTestCase(TestCase):
    """Unit tests for the tournament model at creation time."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/other_clubs.json',
        'chessclubs/tests/fixtures/default_tournament.json',
        'chessclubs/tests/fixtures/other_tournaments.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        # self.tournament.deadline = timezone.now()
        # self.tournament.start_tournament()
        self.second_tournament = Tournament.objects.get(name="Test_Tournament2")

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

    def test_current_phase_cannot_be_blank(self):
        self.tournament._set_current_phase("")
        self._assert_tournament_is_invalid()

    def test_current_phase_must_be_among_choices(self):
        self.tournament._set_current_phase("bad_choice")
        self._assert_tournament_is_invalid()

    def test_successful_change_current_phase(self):
        self.tournament._set_current_phase("Small-Pool-Phase")
        self._assert_tournament_is_valid()

    def _assert_tournament_is_valid(self):
        try:
            self.tournament.full_clean()
        except ValidationError:
            self.fail('Test tournament should be valid')

    def _assert_tournament_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()
