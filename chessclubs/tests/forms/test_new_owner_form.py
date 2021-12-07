"""Unit tests of the new_owner form."""

from django.test import TestCase
from chessclubs.forms import NewOwnerForm
from chessclubs.models import User, Club


class NewOwnerTestCase(TestCase):
    """Unit tests of the new_owner form."""

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.current_owner = User.objects.get(email='johndoe@example.org')
        self.new_owner = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.client.login(email=self.current_owner.email, password='Password123')
        self.form_input = {
            'owner': self.new_owner
        }

    def test_form_has_necessary_fields(self):
        form = NewOwnerForm()
        self.assertIn('owner', form.fields)

    def test_valid_user_form(self):
        form = NewOwnerForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['owner'] = 'YOLO'
        form = NewOwnerForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = NewOwnerForm(instance=self.club, data=self.form_input)
        self.assertEqual(self.club.owner, self.current_owner)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(self.club.owner, self.new_owner)
