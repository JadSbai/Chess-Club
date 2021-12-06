"""Unit tests for TournamentPermission Model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, TournamentPermission, Tournament
from django.contrib.auth.models import Permission
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


class TournamentPermissionModelTestCase(TestCase):
    """Unit tests for the TournamentPermission model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
        'chessclubs/tests/fixtures/default_tournament.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email='johndoe@example.org')
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.base_permission = Permission.objects.get(codename="play_matches")
        self.tournament.assign_tournament_permissions_and_groups()  # Creates all tournament-specific permissions

    def test_tournament_may_not_be_null(self):
        self.tournament = None
        self._assert_creation_is_invalid(IntegrityError)

    def test_base_permission_may_not_be_null(self):
        self.base_permission = None
        self._assert_creation_is_invalid(IntegrityError)

    def test_tournament_delete_causes_tournament_permission_delete(self):
        self.tournament.delete()
        integrity_error_caused = False
        try:
            TournamentPermission.objects.get(tournament=self.tournament, base_permission=self.base_permission)
        except ObjectDoesNotExist:
            integrity_error_caused = True
        self.assertTrue(integrity_error_caused)

    def test_permission_delete_causes_tournament_permission_delete(self):
        self.base_permission.delete()
        integrity_error_caused = False
        try:
            TournamentPermission.objects.get(tournament=self.tournament, base_permission=self.base_permission)
        except ObjectDoesNotExist:
            integrity_error_caused = True
        self.assertTrue(integrity_error_caused)

    def test_unique_combination(self):
        self._assert_creation_is_invalid(IntegrityError)

    def _assert_creation_is_valid(self, exception):
        try:
            TournamentPermission.objects.create(tournament=self.tournament, base_permission=self.base_permission)
        except (exception):
            self.fail('Test tournament permission should be valid')

    def _assert_creation_is_invalid(self, exception):
        with self.assertRaises(exception):
            TournamentPermission.objects.create(tournament=self.tournament, base_permission=self.base_permission)
