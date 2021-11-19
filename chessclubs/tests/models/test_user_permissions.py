"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User
from django.contrib.auth.models import Group, Permission


class UserPermissionsTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.applicants, created = Group.objects.get_or_create(name="applicants")
        self.members, created2 = Group.objects.get_or_create(name="members")
        self.officers, created3 = Group.objects.get_or_create(name="officers")
        self.membersList = Permission.objects.get(codename='access_members_list')
        self.public = Permission.objects.get(codename='show_public_info')
        self.private = Permission.objects.get(codename='show_private_info')
        self.promote = Permission.objects.get(codename='promote')
        self.demote = Permission.objects.get(codename='demote')
        self.transfer_ownership = Permission.objects.get(codename='transfer_ownership')

        self.members_permissions = [self.public, self.membersList]
        self.officers_permissions = self.members_permissions + [self.private]
        self.owner_permissions = self.officers_permissions + [self.promote, self.demote, self.transfer_ownership]

        self.members.permissions.set(self.members_permissions)
        self.officers.permissions.set(self.officers_permissions)

    def makeApplicant(self):
        self.user.groups.clear()
        self.user.groups.add(self.applicants)

    def makeMember(self):
        self.user.groups.clear()
        self.user.groups.add(self.members)

    def makeOfficer(self):
        self.user.groups.clear()
        self.user.groups.add(self.officers)

    def makeOwner(self):
        self.user.groups.clear()
        for permission in self.owner_permissions:
            self.user.user_permissions.add(permission)

    def test_valid_user(self):
        self._assert_user_is_valid()



    def test_applicant_cannot_access_members_list(self):
        self.makeApplicant()
        if self.user.has_perm('chessclubs.access_members_list'):
            self.fail('Applicant should not have access to members list')

    def test_applicant_cannot_access_public_info(self):
        self.makeApplicant()
        if self.user.has_perm('chessclubs.show_public_info'):
            self.fail('Applicant should not have access to public info')

    def test_applicant_cannot_access_private_info(self):
        self.makeApplicant()
        if self.user.has_perm('chessclubs.show_private_info'):
            self.fail('Applicant should not have access to private info')

    def test_applicant_cannot_promote_members(self):
        self.makeApplicant()
        if self.user.has_perm('chessclubs.promote'):
            self.fail('Applicant should not be able to promote members')

    def test_applicant_cannot_demote_officers(self):
        self.makeApplicant()
        if self.user.has_perm('chessclubs.demote'):
            self.fail('Applicant should not be able to demote officers')

    def test_applicant_cannot_transfer_ownership(self):
        self.makeApplicant()
        if self.user.has_perm('chessclubs.transfer_ownership'):
            self.fail('Applicant should not be able to transfer_ownership')

    def test_member_can_access_members_list(self):
        self.makeMember()
        if not self.user.has_perm('chessclubs.access_members_list'):
            self.fail('Member should have access to members list')

    def test_member_can_access_public_info(self):
        self.makeMember()
        if not self.user.has_perm('chessclubs.show_public_info'):
            self.fail('Member should have access to public info')

    def test_member_cannot_access_private_info(self):
        self.makeMember()
        if self.user.has_perm('chessclubs.show_private_info'):
            self.fail('Member should not have access to private info')

    def test_member_cannot_promote_members(self):
        self.makeMember()
        if self.user.has_perm('chessclubs.promote'):
            self.fail('Member should not be able to promote members')

    def test_member_cannot_demote_officers(self):
        self.makeMember()
        if self.user.has_perm('chessclubs.demote'):
            self.fail('Member should not be able to demote officers')

    def test_member_cannot_transfer_ownership(self):
        self.makeMember()
        if self.user.has_perm('chessclubs.transfer_ownership'):
            self.fail('Member should not be able to transfer_ownership')

    def test_officer_can_access_members_list(self):
        self.makeOfficer()
        if not self.user.has_perm('chessclubs.access_members_list'):
            self.fail('Officer should have access to members list')

    def test_officer_can_access_public_info(self):
        self.makeOfficer()
        if not self.user.has_perm('chessclubs.show_public_info'):
            self.fail('Officer should have access to public info')

    def test_officer_cannot_access_private_info(self):
        self.makeOfficer()
        if not self.user.has_perm('chessclubs.show_private_info'):
            self.fail('Officer should have access to private info')

    def test_officer_cannot_promote_members(self):
        self.makeOfficer()
        if self.user.has_perm('chessclubs.promote'):
            self.fail('Officer should not be able to promote members')

    def test_officer_cannot_demote_officers(self):
        self.makeOfficer()
        if self.user.has_perm('chessclubs.demote'):
            self.fail('Officer should not be able to demote officers')

    def test_officer_cannot_transfer_ownership(self):
        self.makeOfficer()
        if self.user.has_perm('chessclubs.transfer_ownership'):
            self.fail('Officer should not be able to transfer_ownership')

    def test_owner_can_access_members_list(self):
        self.makeOwner()
        if not self.user.has_perm('chessclubs.access_members_list'):
            self.fail('Owner should have access to members list')

    def test_owner_can_access_public_info(self):
        self.makeOwner()
        if not self.user.has_perm('chessclubs.show_public_info'):
            self.fail('Owner should have access to public info')

    def test_owner_cannot_access_private_info(self):
        self.makeOwner()
        if not self.user.has_perm('chessclubs.show_private_info'):
            self.fail('Owner should have access to private info')

    def test_owner_cannot_promote_members(self):
        self.makeOwner()
        if not self.user.has_perm('chessclubs.promote'):
            self.fail('Owner should be able to promote members')

    def test_owner_cannot_demote_officers(self):
        self.makeOwner()
        if not self.user.has_perm('chessclubs.demote'):
            self.fail('Owner should be able to demote officers')

    def test_owner_cannot_transfer_ownership(self):
        self.makeOwner()
        if not self.user.has_perm('chessclubs.transfer_ownership'):
            self.fail('Owner should be able to transfer_ownership')

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
