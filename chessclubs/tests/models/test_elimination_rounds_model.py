"""Unit tests for the Elimination rounds model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import Tournament, EliminationRounds, User
from django.utils import timezone

class EliminationRoundsModelTestCase(TestCase):
    """Unit tests for the tournament model at creation time."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/default_tournament.json',
        'chessclubs/tests/fixtures/default_elimination_round.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.elimination_round = EliminationRounds.objects.get(pk=self.tournament.pk)
        self.player1 = User.objects.get(email="janedoe@example.org")
        self.player2 = User.objects.get(email="petrapickles@example.org")
        self.elimination_round.add_players([self.player2, self.player1])
        self.elimination_round.create_schedule()


    def _assert_round_is_valid(self):
        try:
            self.tournament.full_clean()
        except ValidationError:
            self.fail('Test tournament should be valid')

    def _assert_round_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()
