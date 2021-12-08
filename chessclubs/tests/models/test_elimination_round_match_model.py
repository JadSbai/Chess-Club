from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, Tournament, EliminationRoundMatch, EliminationRounds
from chessclubs.tests.helpers import ClubGroupTester


class MatchModelTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/default_elimination_round.json',
                'chessclubs/tests/fixtures/default_match.json',
                'chessclubs/tests/fixtures/default_elimination_match.json',
                ]

    def setUp(self):
        self.organiser = User.objects.get(email='johndoe@example.org')
        self.player1 = User.objects.get(email="janedoe@example.org")
        self.player2 = User.objects.get(email="petrapickles@example.org")
        self.club = Club.objects.get(name="Test_Club")
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_member(self.player1)
        self.group_tester.make_member(self.player2)
        self.tournament.add_participant(self.player1)
        self.tournament.add_participant(self.player2)
        self.elimination_round = EliminationRounds.objects.get(pk=1)
        self.elimination_round.add_players([self.player1, self.player2])
        self.elimination_match = EliminationRoundMatch.objects.get(pk=1)

    def test_cannot_create_match_with_same_players(self):
        with self.assertRaises(ValueError):
            EliminationRoundMatch.objects.create_match(tournament=self.tournament, player1=self.player1, player2=self.player1)

    def test_cannot_create_match_with_organiser(self):
        with self.assertRaises(ValueError):
            EliminationRoundMatch.objects.create_match(tournament=self.tournament, player1=self.tournament.organiser,
                                               player2=self.player1)

    def test_enter_winner_while_closed(self):
        self.elimination_match.close_match()
        before = self.elimination_match.elimination_round.number_of_players()
        winner = self.elimination_match.enter_winner(self.player1)
        after = self.elimination_match.elimination_round.number_of_players()
        self.assertFalse(self.elimination_match.is_open())
        self.assertEqual(winner, None)
        self.assertEqual(before, after)


    def test_enter_winner_with_non_player(self):
        before = self.elimination_match.elimination_round.number_of_players()
        winner = self.elimination_match.enter_winner(self.organiser)
        after = self.elimination_match.elimination_round.number_of_players()
        self.assertEqual(winner, None)
        self.assertTrue(self.elimination_match.is_open())
        self.assertEqual(before, after)

    def test_successful_enter_winner(self):
        before = self.elimination_match.elimination_round.number_of_players()
        winner = self.elimination_match.enter_winner(self.player2)
        after = self.elimination_match.elimination_round.number_of_players()
        self.assertFalse(self.elimination_match.is_open())
        self.assertEqual(winner, self.player2)
        self.assertEqual(before - 1, after)


    def _assert_match_is_valid(self):
        try:
            self.elimination_match.full_clean()
        except ValidationError:
            self.fail('Test elimination match should be valid')

    def _assert_match_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.elimination_match.full_clean()
