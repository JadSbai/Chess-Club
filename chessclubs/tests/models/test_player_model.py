"""Unit tests for the Player model."""
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from chessclubs.models import User, Player, Tournament

class PlayerModelTestCase(TestCase):
    """Unit tests for the Player model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_player.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/default_tournament.json',
        'chessclubs/tests/fixtures/other_players.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.player = Player.objects.get(pk=1)
        self.player2 = Player.objects.get(pk=2)
        self.player3 = Player.objects.get(pk=3)
        self.player4 = Player.objects.get(pk=4)
        self.tournament = Tournament.objects.get(name="Test_Tournament")

    def test_unique_combination(self):
        with self.assertRaises(IntegrityError):
            Player.objects.create(tournament=self.tournament, user=self.player.user)

    def test_win(self):
        before = self.player.get_points()
        self.player.win()
        after = self.player.get_points()
        self.assertEqual(before + 1, after)

    def test_draw(self):
        before = self.player.get_points()
        self.player.draw()
        after = self.player.get_points()
        self.assertEqual(before + 0.5, after)

    def test_ordered_by_points(self):
        self.player4.win()
        self.player4.win()
        self.player3.draw()
        self.player2.win()
        self.player3.win()
        self.player.draw()
        players = Player.objects.all()
        self.assertTrue(players[0], self.player4)
        self.assertTrue(players[1], self.player3)
        self.assertTrue(players[2], self.player2)
        self.assertTrue(players[3], self.player)

