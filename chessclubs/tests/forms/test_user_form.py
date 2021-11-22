"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from chessclubs.forms import UserForm
from chessclubs.models import User

class UserFormTestCase(TestCase):
    """Unit tests of the user form."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'bio': 'My bio',
            'chess_experience': 'Intermediate',
            'personal_statement': 'I am the best'
        }

    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('bio', form.fields)
        self.assertIn('chess_experience', form.fields)
        self.assertIn('personal_statement', form.fields)

    def test_valid_user_form(self):
        form = UserForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['chess_experience'] = ''
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(email='johndoe@example.org')
        form = UserForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'johndoe@example.org')
        self.assertEqual(user.bio, 'My bio')
        self.assertEqual(user.chess_experience, 'Intermediate')
        self.assertEqual(user.personal_statement, 'I have a whiteboard')

