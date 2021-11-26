"""Unit tests for the club model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club

class clubModelTestCase(TestCase):
    """Unit tests for the club model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email='johndoe@example.org')
        self.club = Club(
            owner=self.user,
            name="Test name",
            location = "London",
            description = "The quick brown fow jumps over the lazy dog"
        )


    def test_owner_must_not_be_blank(self):
        self.club.owner=None
        self._assert_club_is_invalid()

    def test_name_must_not_be_blank(self):
        self.club.name = ''
        self._assert_club_is_invalid()

    def test_name_must_be_unique(self):
        second_club = Club(owner=User.objects.get(email='janedoe@example.org'),
            name="Test name2",
            location = "London",
            description = "The quick brown fow jumps over the lazy dog")
        self.club.name = second_club.name
        self._assert_club_is_invalid()


    def test_location_must_not_be_blank(self):
        self.club.location =''
        self._assert_club_is_invalid()


    def test_name_may_contain_50_characters(self):
        self.club.name = 'x' * 50
        self._assert_club_is_valid()

    def test_name_must_not_contain_more_than_50_characters(self):
        self.club.name = 'x' * 51
        self._assert_club_is_invalid()


    def test_location_must_not_be_blank(self):
        self.club.location = ''
        self._assert_club_is_invalid()


    def test_description_may_be_blank(self):
        self.club.description = ''
        self._assert_club_is_valid()

    def test_description_need_not_be_unique(self):
        second_club = Club(owner=User.objects.get(email='janedoe@example.org'),
            name="Test name2",
            location = "London",
            description = "The quick brown fow jumps over the lazy dog")
        self.club.description = second_club.description
        self._assert_club_is_valid()

    def test_description_may_contain_520_characters(self):
        self.club.description = 'x' * 520
        self._assert_club_is_valid()

    def test_description_must_not_contain_more_than_520_characters(self):
        self.club.description = 'x' * 521
        self._assert_club_is_invalid()

    def test_location_may_contain_50_characters(self):
        self.club.location = 'x' * 50
        self._assert_club_is_valid()

    def test_location_must_not_contain_more_than_50_characters(self):
        self.club.location = 'x' * 51
        self._assert_club_is_invalid()

    def test_location_need_not_be_unique(self):
        second_club = Club(owner=User.objects.get(email='janedoe@example.org'),
                           name="Test name2",
                           location="London",
                           description="The quick brown fow jumps over the lazy dog")
        self.club.location = second_club.location
        self._assert_club_is_valid()

    def test_description_may_contain_520_characters(self):
        self.club.personal_statement = 'x' * 500
        self._assert_club_is_valid()

    def test_description_must_not_contain_more_than_520_characters(self):
        self.club.personal_statement = 'x' * 521
        self._assert_club_is_invalid()

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()



