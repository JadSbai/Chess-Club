"""Unit tests of the log in form."""
from django import forms
from django.test import TestCase
from chessclubs.models import User,Club
from chessclubs.forms import ClubForm

class ClubFormTestCase(TestCase):
    """Unit tests of the club form."""
    fixtures = ['chessclubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(email="johndoe@example.org")

    def test_valid_post_form(self):
        input={'name': 'y'*40, 'description': 'x'*200, 'location': 'z'*20}
        form = ClubForm(data=input)
        self.assertTrue(form.is_valid())

    def test_too_long_name_is_invalid(self):
        input = {'name': 'y' * 70, 'description': 'x' * 200, 'location': 'z' * 20}
        form = ClubForm(data=input)
        self.assertFalse(form.is_valid())

    def test_too_long_description_is_invalid(self):
        input = {'name': 'y' * 40, 'description': 'x' * 700, 'location': 'z' * 20}
        form = ClubForm(data=input)
        self.assertFalse(form.is_valid())

    def test_too_long_location_is_invalid(self):
        input = {'name': 'y' * 40, 'description': 'x' * 200, 'location': 'z' * 70}
        form = ClubForm(data=input)
        self.assertFalse(form.is_valid())

