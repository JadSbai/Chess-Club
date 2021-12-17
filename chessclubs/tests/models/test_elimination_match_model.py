from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, Tournament, EliminationMatch, Player, EliminationRounds
from chessclubs.tests.helpers import ClubGroupTester


class EliminationMatchModelTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/elimination_players.json',
                'chessclubs/tests/fixtures/default_elimination_round.json',
                'chessclubs/tests/fixtures/default_elimination_match.json',
                ]

    def setUp(self):
        self.organiser = User.objects.get(email='johndoe@example.org')
        self.player1 = Player.objects.get(pk=2)
        self.player2 = Player.objects.get(pk=3)
        self.other_player = Player.objects.get(pk=3)
        self.club = Club.objects.get(name="Test_Club")
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_member(self.player1.user)
        self.group_tester.make_member(self.player2.user)
        self.elimination_match = EliminationMatch.objects.get(pk=1)

    def test_cannot_create_match_with_same_players(self):
        with self.assertRaises(ValueError):
            EliminationMatch.objects.create_match(tournament=self.tournament, player1=self.player1,
                                                  player2=self.player1)

    def test_cannot_create_match_with_organiser(self):
        with self.assertRaises(ValueError):
            EliminationMatch.objects.create_match(tournament=self.tournament, player1=self.tournament.organiser,
                                                  player2=self.player1)

    def test_successful_enter_winner(self):
        winner = self.elimination_match.enter_winner(self.player2)
        self.assertFalse(self.elimination_match.is_open())
        self.assertEqual(winner, self.player2)

    def _assert_match_is_valid(self):
        try:
            self.elimination_match.full_clean()
        except ValidationError:
            self.fail('Test elimination match should be valid')

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.elimination_match.full_clean()
