"""Unit tests for the club model """

from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club, ClubPermission
from django.contrib.auth.models import Permission
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


class ClubPermissionModelTestCase(TestCase):
    """Unit tests for the club model """

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email='johndoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.base_permission = Permission.objects.get(codename="promote")


    def test_club_may_not_be_null(self):
        self.club = None
        self._assert_creation_is_invalid(IntegrityError)


    def test_base_permission_may_not_be_null(self):
        self.base_permission = None
        self._assert_creation_is_invalid(IntegrityError)

    def test_club_delete_causes_club_permission_delete(self):
        ClubPermission.objects.create(club=self.club, base_permission=self.base_permission)
        self.club.delete()
        integrity_error_caused = False
        try:
            ClubPermission.objects.get(club=self.club, base_permission=self.base_permission)
        except ObjectDoesNotExist:
            integrity_error_caused = True
        self.assertTrue(integrity_error_caused)

    def test_permission_delete_causes_club_permission_delete(self):
        ClubPermission.objects.create(club=self.club, base_permission=self.base_permission)
        self.base_permission.delete()
        integrity_error_caused = False
        try:
            ClubPermission.objects.get(club=self.club, base_permission=self.base_permission)
        except ObjectDoesNotExist:
            integrity_error_caused = True
        self.assertTrue(integrity_error_caused)

    def test_unique_combination(self):
        ClubPermission.objects.create(club=self.club, base_permission=self.base_permission)
        self._assert_creation_is_invalid(IntegrityError)

    def _assert_creation_is_valid(self, exception):
        try:
            ClubPermission.objects.create(club=self.club, base_permission=self.base_permission)
        except (exception):
            self.fail('Test club permission should be valid')

    def _assert_creation_is_invalid(self, exception):
        with self.assertRaises(exception):
            ClubPermission.objects.create(club=self.club, base_permission=self.base_permission)
