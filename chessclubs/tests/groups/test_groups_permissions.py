"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User
from chessclubs.tests.helpers import GroupTester



class UserPermissionsTestCase(TestCase):
    """Unit tests for the Group permissions. Assess that groups possess the appropriate permissions"""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester = GroupTester()

    def test_applicant_cannot_access_members_list(self):
        self.group_tester.make_applicant(self.user)
        if self.user.has_perm('chessclubs.access_members_list'):
            self.fail('Applicant should not have access to members list')

    def test_applicant_cannot_access_public_info(self):
        self.group_tester.make_applicant(self.user)
        if self.user.has_perm('chessclubs.show_public_info'):
            self.fail('Applicant should not have access to public info')

    def test_applicant_cannot_access_private_info(self):
        self.group_tester.make_applicant(self.user)
        if self.user.has_perm('chessclubs.show_private_info'):
            self.fail('Applicant should not have access to private info')

    def test_applicant_cannot_promote_members(self):
        self.group_tester.make_applicant(self.user)
        if self.user.has_perm('chessclubs.promote'):
            self.fail('Applicant should not be able to promote members')

    def test_applicant_cannot_demote_officers(self):
        self.group_tester.make_applicant(self.user)
        if self.user.has_perm('chessclubs.demote'):
            self.fail('Applicant should not be able to demote officers')

    def test_applicant_cannot_transfer_ownership(self):
        self.group_tester.make_applicant(self.user)
        if self.user.has_perm('chessclubs.transfer_ownership'):
            self.fail('Applicant should not be able to transfer_ownership')

    def test_member_can_access_members_list(self):
        self.group_tester.make_member(self.user)
        if not self.user.has_perm('chessclubs.access_members_list'):
            self.fail('Member should have access to members list')

    def test_member_can_access_public_info(self):
        self.group_tester.make_member(self.user)
        if not self.user.has_perm('chessclubs.show_public_info'):
            self.fail('Member should have access to public info')

    def test_member_cannot_access_private_info(self):
        self.group_tester.make_member(self.user)
        if self.user.has_perm('chessclubs.show_private_info'):
            self.fail('Member should not have access to private info')

    def test_member_cannot_promote_members(self):
        self.group_tester.make_member(self.user)
        if self.user.has_perm('chessclubs.promote'):
            self.fail('Member should not be able to promote members')

    def test_member_cannot_demote_officers(self):
        self.group_tester.make_member(self.user)
        if self.user.has_perm('chessclubs.demote'):
            self.fail('Member should not be able to demote officers')

    def test_member_cannot_transfer_ownership(self):
        self.group_tester.make_member(self.user)
        if self.user.has_perm('chessclubs.transfer_ownership'):
            self.fail('Member should not be able to transfer_ownership')

    def test_officer_can_access_members_list(self):
        self.group_tester.make_officer(self.user)
        if not self.user.has_perm('chessclubs.access_members_list'):
            self.fail('Officer should have access to members list')

    def test_officer_can_access_public_info(self):
        self.group_tester.make_officer(self.user)
        if not self.user.has_perm('chessclubs.show_public_info'):
            self.fail('Officer should have access to public info')

    def test_officer_cannot_access_private_info(self):
        self.group_tester.make_officer(self.user)
        if not self.user.has_perm('chessclubs.show_private_info'):
            self.fail('Officer should have access to private info')

    def test_officer_cannot_promote_members(self):
        self.group_tester.make_officer(self.user)
        if self.user.has_perm('chessclubs.promote'):
            self.fail('Officer should not be able to promote members')

    def test_officer_cannot_demote_officers(self):
        self.group_tester.make_officer(self.user)
        if self.user.has_perm('chessclubs.demote'):
            self.fail('Officer should not be able to demote officers')

    def test_officer_cannot_transfer_ownership(self):
        self.group_tester.make_officer(self.user)
        if self.user.has_perm('chessclubs.transfer_ownership'):
            self.fail('Officer should not be able to transfer_ownership')

    def test_owner_can_access_members_list(self):
        self.group_tester.make_owner(self.user)
        if not self.user.has_perm('chessclubs.access_members_list'):
            self.fail('Owner should have access to members list')

    def test_owner_can_access_public_info(self):
        self.group_tester.make_owner(self.user)
        if not self.user.has_perm('chessclubs.show_public_info'):
            self.fail('Owner should have access to public info')

    def test_owner_can_access_private_info(self):
        self.group_tester.make_owner(self.user)
        if not self.user.has_perm('chessclubs.show_private_info'):
            self.fail('Owner should have access to private info')

    def test_owner_can_promote_members(self):
        self.group_tester.make_owner(self.user)
        if not self.user.has_perm('chessclubs.promote'):
            self.fail('Owner should be able to promote members')

    def test_owner_can_demote_officers(self):
        self.group_tester.make_owner(self.user)
        if not self.user.has_perm('chessclubs.demote'):
            self.fail('Owner should be able to demote officers')

    def test_owner_can_transfer_ownership(self):
        self.group_tester.make_owner(self.user)
        if not self.user.has_perm('chessclubs.transfer_ownership'):
            self.fail('Owner should be able to transfer_ownership')

    def test_denied_applicant_cannot_access_members_list(self):
        self.group_tester.make_denied_applicant(self.user)
        if self.user.has_perm('chessclubs.access_members_list'):
            self.fail('Applicant should not have access to members list')

    def test_denied_applicant_cannot_access_public_info(self):
        self.group_tester.make_denied_applicant(self.user)
        if self.user.has_perm('chessclubs.show_public_info'):
            self.fail('Applicant should not have access to public info')

    def test_denied_applicant_cannot_access_private_info(self):
        self.group_tester.make_denied_applicant(self.user)
        if self.user.has_perm('chessclubs.show_private_info'):
            self.fail('Applicant should not have access to private info')

    def test_denied_applicant_cannot_promote_members(self):
        self.group_tester.make_denied_applicant(self.user)
        if self.user.has_perm('chessclubs.promote'):
            self.fail('Applicant should not be able to promote members')

    def test_denied_applicant_cannot_demote_officers(self):
        self.group_tester.make_denied_applicant(self.user)
        if self.user.has_perm('chessclubs.demote'):
            self.fail('Applicant should not be able to demote officers')

    def test_denied_applicant_cannot_transfer_ownership(self):
        self.group_tester.make_denied_applicant(self.user)
        if self.user.has_perm('chessclubs.transfer_ownership'):
            self.fail('Applicant should not be able to transfer_ownership')
