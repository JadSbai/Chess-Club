"""Unit tests for the club model."""
from django.core.exceptions import ValidationError
from django.test import TestCase

from chessclubs.models import User, Club


class ClubModelTestCase(TestCase):
    """Unit tests for the club model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/other_clubs.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email='johndoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.second_club = Club.objects.get(name="Test_Club2")

    def test_owner_must_not_be_blank(self):
        self.club.owner = None
        self._assert_club_is_invalid()

    def test_name_must_not_be_blank(self):
        self.club.name = ''
        self._assert_club_is_invalid()

    def test_name_must_be_unique(self):
        self.club.name = self.second_club.name
        self._assert_club_is_invalid()

    def test_location_must_not_be_blank(self):
        self.club.location = ''
        self._assert_club_is_invalid()

    def test_name_may_contain_50_characters(self):
        self.club.name = 'x' * 50
        self._assert_club_is_valid()

    def test_name_must_not_contain_more_than_50_characters(self):
        self.club.name = 'x' * 51
        self._assert_club_is_invalid()

    def test_description_may_be_blank(self):
        self.club.description = ''
        self._assert_club_is_valid()

    def test_description_need_not_be_unique(self):
        self.club.description = self.second_club.description
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
        self.club.location = self.second_club.location
        self._assert_club_is_valid()

    def test_members_field_returns_current_members(self):
        self.assertEqual(self.club.member_count(), 0)
        self.club.add_member(User.objects.get(email='janedoe@example.org'))
        self.assertEqual(self.club.member_count(), 1)
        self.club.remove_member(User.objects.get(email='janedoe@example.org'))
        self.assertEqual(self.club.member_count(), 0)
        self.club.toggle_membership(User.objects.get(email='janedoe@example.org'))
        self.assertEqual(self.club.member_count(), 1)

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except ValidationError:
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()
