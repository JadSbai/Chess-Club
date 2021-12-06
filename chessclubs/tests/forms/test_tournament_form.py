"""Unit tests of the tournament form."""
from django import forms
from django.test import TestCase
from chessclubs.models import User,Club, Tournament
from chessclubs.forms import TournamentForm
from django.utils import timezone



class tournamentTestCase(TestCase):
    """Unit tests of the tournament form."""
    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/other_clubs.json',
        'chessclubs/tests/fixtures/default_tournament.json',
        'chessclubs/tests/fixtures/other_tournaments.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.org")

    def test_valid_tournament_form(self):
        input={'name': 'y'*40, 'location': 'x'*40, 'capacity':20, 'deadline':(timezone.now()+timezone.timedelta(days=1))}
        form = TournamentForm(data=input)
        self.assertTrue(form.is_valid())

    def test_today_is_invalid(self):
        input = {'name': 'y' * 40, 'location': 'x' * 40, 'capacity': 20,
                 'deadline': (timezone.now())}
        form = TournamentForm(data=input)
        self.assertFalse(form.is_valid())



