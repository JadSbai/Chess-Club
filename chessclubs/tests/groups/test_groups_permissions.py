"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User
from django.contrib.auth.models import Group
from chessclubs.groups import members_permissions, officers_permissions, owner_permissions, members, officers, applicants


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

        self.members.permissions.set(members_permissions)
        self.officers.permissions.set(officers_permissions)

    def makeApplicant(self):
        self.user.groups.clear()
        self.user.groups.add(applicants)

    def makeMember(self):
        self.user.groups.clear()
        self.user.groups.add(members)

    def makeOfficer(self):
        self.user.groups.clear()
        self.user.groups.add(officers)

    def makeOwner(self):
        self.user.groups.clear()
        for permission in owner_permissions:
            self.user.user_permissions.add(permission)

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
