"""Unit tests of the club form."""
from django import forms
from django.test import TestCase
from chessclubs.forms import EditClubInformationForm
from chessclubs.models import User, Club

class EditClubFormTestCase(TestCase):
    """Unit tests of the club form."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.form_input = {
            'description': 'New Standards',
            'location': 'Zimbabwe',
        }

    def test_form_has_necessary_fields(self):
        form = EditClubInformationForm()
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)

    def test_valid_user_form(self):
        form = EditClubInformationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['location'] = ''
        form = EditClubInformationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        club = Club.objects.get(name='Test_Club')
        form = EditClubInformationForm(instance=club, data=self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(club.description, 'New Standards')
        self.assertEqual(club.location, 'Zimbabwe')
