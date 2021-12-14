"""Unit tests of the club form."""
from django import forms
from django.test import TestCase
from chessclubs.models import User,Club
from chessclubs.forms import ClubForm

class ClubFormTestCase(TestCase):
    """Unit tests of the club form."""
    fixtures = ['chessclubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.org")
        self.form_input = {
            'name': 'Test Club',
            'description': 'This is a short description of the club',
            'location': 'London',
        }

    def test_valid_club_form(self):
        form = ClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['name'] = 'y' * 60
        form = ClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = ClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        description_widget = form.fields['description'].widget
        self.assertTrue(isinstance(description_widget, forms.Textarea))
        self.assertIn('location', form.fields)

    def test_form_must_save_correctly(self):
        form = ClubForm(data=self.form_input)
        before_count = Club.objects.count()
        form.save(self.user)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count+1)
        club = Club.objects.get(name='Test Club')
        self.assertEqual(club.description, 'This is a short description of the club')
        self.assertEqual(club.location, 'London')
        self.assertEqual(club.owner, self.user)
        self.assertEqual(club.member_count(), 1)
