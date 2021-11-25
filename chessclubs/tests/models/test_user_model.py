"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User

class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_email_is_unique_identifier(self):
        if self.user.USERNAME_FIELD != self.user.get_email_field_name():
            self.fail('Username should be the same as email')

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = User.objects.get(email='janedoe@example.org')
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = User.objects.get(email='janedoe@example.org')
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(email='janedoe@example.org')
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_bio_may_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):
        second_user = User.objects.get(email='janedoe@example.org')
        self.user.bio = second_user.bio
        self._assert_user_is_valid()

    def test_bio_may_contain_520_characters(self):
        self.user.bio = 'x' * 520
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_520_characters(self):
        self.user.bio = 'x' * 521
        self._assert_user_is_invalid()

    # def test_chess_experience_must_not_be_blank(self):
    #     self.user.chess_experience = ''
    #     self._assert_user_is_invalid()
    #
    # def test_chess_experience_need_not_be_unique(self):
    #     second_user = User.objects.get(email='janedoe@example.org')
    #     self.user.chess_experience = second_user.chess_experience
    #     self._assert_user_is_valid()
    #
    # def test_chess_experience_may_contain_50_characters(self):
    #     self.user.chess_experience = 'x' * 50
    #     self._assert_user_is_valid()

    def test_chess_experience_must_not_contain_more_than_50_characters(self):
        self.user.chess_experience = 'x' * 51
        self._assert_user_is_invalid()

    def test_personal_statement_must_not_be_blank(self):
        self.user.personal_statement = ''
        self._assert_user_is_invalid()

    def test_personal_statement_need_not_be_unique(self):
        second_user = User.objects.get(email='janedoe@example.org')
        self.user.personal_statement = second_user.personal_statement
        self._assert_user_is_valid()

    def test_personal_statement_may_contain_500_characters(self):
        self.user.personal_statement = 'x' * 500
        self._assert_user_is_valid()

    def test_personal_statement_must_not_contain_more_than_500_characters(self):
        self.user.personal_statement = 'x' * 501
        self._assert_user_is_invalid()

    def test_chess_experience_must_not_be_anything_other_than_given_choices(self):
        self.user.chess_experience = 'Nonexisting'
        self._assert_user_is_invalid()

    def test_chess_experience_must_be_from_given_choices(self):
        self.user.chess_experience = 'Novice'
        self._assert_user_is_valid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
