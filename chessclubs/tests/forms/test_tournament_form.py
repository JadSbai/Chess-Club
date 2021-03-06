"""Unit tests of the tournament form."""
from django import forms
from django.test import TestCase
from chessclubs.models import User,Club, Tournament
from chessclubs.forms import TournamentForm
from django.utils import timezone

class TournamentFormTestCase(TestCase):
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
        self.club = Club.objects.get(name="Test_Club")
        self.deadline = timezone.now() + timezone.timedelta(days=1)
        self.form_input = {
            'name': 'Test Tournament',
            'description': 'Some short description',
            'location': 'x' * 40,
            'max_capacity': 20,
            'deadline': self.deadline
        }

    def test_valid_tournament_form(self):
        form = TournamentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_today_is_invalid(self):
        self.form_input['deadline'] = timezone.now()
        form = TournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = TournamentForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        description_widget = form.fields['description'].widget
        self.assertTrue(isinstance(description_widget, forms.Textarea))
        self.assertIn('location', form.fields)
        self.assertIn('max_capacity', form.fields)
        max_capacity_widget = form.fields['max_capacity'].widget
        self.assertTrue(isinstance(max_capacity_widget, forms.TextInput))
        self.assertIn('deadline', form.fields)
        deadline_widget = form.fields['deadline'].widget
        self.assertTrue(isinstance(deadline_widget, forms.DateTimeInput))

    def test_form_uses_model_validation(self):
        self.form_input['max_capacity'] = -100
        form = TournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = TournamentForm(data=self.form_input)
        before_count = Tournament.objects.count()
        tournament = form.save(club=self.club, organiser=self.user)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(tournament.name, 'Test Tournament')
        self.assertEqual(tournament.description, 'Some short description')
        self.assertEqual(tournament.location, 'x' * 40)
        self.assertEqual(tournament.max_capacity, 20)
        self.assertEqual(tournament.deadline, self.deadline)
        self.assertEqual(tournament.organiser, self.user)




