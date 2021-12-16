"""Unit tests for the o model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester


class ClubGroupPermissionsTestCase(TestCase):
    """Unit tests for the Club Group permissions. Assess that groups in clubs possess the appropriate permissions"""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
    ]

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.get(email='johndoe@example.org')
        cls.other_user = User.objects.get(email='janedoe@example.org')
        cls.club = Club.objects.get(name="Test_Club")
        cls.group_tester = ClubGroupTester(cls.club)

    def test_applicant_can_access_club_info(self):
        self.group_tester.make_applicant(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_info', self.club):
            self.fail('Applicant should have access to club info')

    def test_applicant_can_access_club_owner_public_info(self):
        self.group_tester.make_applicant(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_owner_public_info', self.club):
            self.fail('Applicant should have access to cub owner public info')

    def test_applicant_cannot_manage_applications(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.manage_applications', self.club):
            self.fail('Applicant should be able to manage applications')

    def test_applicant_cannot_access_members_list(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.access_members_list', self.club):
            self.fail('Applicant should not have access to members list')

    def test_applicant_cannot_access_public_info(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.show_public_info', self.club):
            self.fail('Applicant should not have access to public info')

    def test_applicant_cannot_access_private_info(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.show_private_info', self.club):
            self.fail('Applicant should not have access to private info')

    def test_applicant_cannot_promote_members(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.promote', self.club):
            self.fail('Applicant should not be able to promote members')

    def test_applicant_cannot_demote_officers(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.demote', self.club):
            self.fail('Applicant should not be able to demote officers')

    def test_applicant_cannot_transfer_ownership(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.transfer_ownership', self.club):
            self.fail('Applicant should not be able to transfer_ownership')

    def test_applicant_cannot_apply_to_club(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.apply_to_club', self.club):
            self.fail('Applicant should not be able to apply to club')

    def test_applicant_cannot_acknowledge_application_response(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.acknowledge_response', self.club):
            self.fail('Applicant should not be able to acknowledge response')

    def test_applicant_cannot_ban(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.ban', self.club):
            self.fail('Applicant should not be able to ban a user')

    def test_applicant_cannot_leave(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.leave', self.club):
            self.fail('Applicant should not be able to leave a club')

    def test_applicant_cannot_create_tournament(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.create_tournament', self.club):
            self.fail('Applicant should not be able to create tournament')

    def test_applicant_cannot_apply_tournament(self):
        self.group_tester.make_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.join_tournament', self.club):
            self.fail('Applicant should not be able to join a tournament')

    def test_member_can_access_club_info(self):
        self.group_tester.make_member(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_info', self.club):
            self.fail('Member should have access to club info')

    def test_member_can_access_club_owner_public_info(self):
        self.group_tester.make_member(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_owner_public_info', self.club):
            self.fail('Member should have access to cub owner public info')

    def test_member_cannot_manage_applications(self):
        self.group_tester.make_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.manage_applications', self.club):
            self.fail('Member should be able to manage applications')

    def test_member_can_access_members_list(self):
        self.group_tester.make_member(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_members_list', self.club):
            self.fail('Member should have access to members list')

    def test_member_can_access_public_info(self):
        self.group_tester.make_member(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.show_public_info', self.club):
            self.fail('Member should have access to public info')

    def test_member_cannot_access_private_info(self):
        self.group_tester.make_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.show_private_info', self.club):
            self.fail('Member should not have access to private info')

    def test_member_cannot_promote_members(self):
        self.group_tester.make_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.promote', self.club):
            self.fail('Member should not be able to promote members')

    def test_member_cannot_demote_officers(self):
        self.group_tester.make_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.demote', self.club):
            self.fail('Member should not be able to demote officers')

    def test_member_cannot_transfer_ownership(self):
        self.group_tester.make_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.transfer_ownership', self.club):
            self.fail('Member should not be able to transfer_ownership')

    def test_member_cannot_apply_to_club(self):
        self.group_tester.make_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.apply_to_club', self.club):
            self.fail('Member should not be able to apply to club')

    def test_member_cannot_acknowledge_application_response(self):
        self.group_tester.make_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.acknowledge_response', self.club):
            self.fail('Member should not be able to acknowledge response')

    def test_member_cannot_ban(self):
        self.group_tester.make_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.ban', self.club):
            self.fail('Member should not be able to ban a user')

    def test_member_can_leave(self):
        self.group_tester.make_member(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.leave', self.club):
            self.fail('Member should not be able to leave a club')

    def test_member_cannot_create_tournament(self):
        self.group_tester.make_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.create_tournament', self.club):
            self.fail('Member should not be able to create tournament')

    def test_member_can_apply_tournament(self):
        self.group_tester.make_member(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.join_tournament', self.club):
            self.fail('Member should be able to apply to a tournament')

    def test_officer_can_access_club_info(self):
        self.group_tester.make_officer(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_info', self.club):
            self.fail('Officer should have access to club info')

    def test_officer_can_access_club_owner_public_info(self):
        self.group_tester.make_officer(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_owner_public_info', self.club):
            self.fail('Officer should have access to cub owner public info')

    def test_officer_can_manage_applications(self):
        self.group_tester.make_officer(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.manage_applications', self.club):
            self.fail('Officer should be able to manage applications')

    def test_officer_can_access_members_list(self):
        self.group_tester.make_officer(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_members_list', self.club):
            self.fail('Officer should have access to members list')

    def test_officer_can_access_public_info(self):
        self.group_tester.make_officer(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.show_public_info', self.club):
            self.fail('Officer should have access to public info')

    def test_officer_cannot_access_private_info(self):
        self.group_tester.make_officer(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.show_private_info', self.club):
            self.fail('Officer should have access to private info')

    def test_officer_cannot_promote_members(self):
        self.group_tester.make_officer(self.other_user)
        if self.other_user.has_club_perm('chessclubs.promote', self.club):
            self.fail('Officer should not be able to promote members')

    def test_officer_cannot_demote_officers(self):
        self.group_tester.make_officer(self.other_user)
        if self.other_user.has_club_perm('chessclubs.demote', self.club):
            self.fail('Officer should not be able to demote officers')

    def test_officer_cannot_transfer_ownership(self):
        self.group_tester.make_officer(self.other_user)
        if self.other_user.has_club_perm('chessclubs.transfer_ownership', self.club):
            self.fail('Officer should not be able to transfer_ownership')

    def test_officer_cannot_apply_to_club(self):
        self.group_tester.make_officer(self.other_user)
        if self.other_user.has_club_perm('chessclubs.apply_to_club', self.club):
            self.fail('Officer should not be able to apply to club')

    def test_officer_cannot_acknowledge_application_response(self):
        self.group_tester.make_officer(self.other_user)
        if self.other_user.has_club_perm('chessclubs.acknowledge_response', self.club):
            self.fail('Officer should not be able to acknowledge response')

    def test_officer_cannot_ban(self):
        self.group_tester.make_officer(self.other_user)
        if self.other_user.has_club_perm('chessclubs.ban', self.club):
            self.fail('Officer should not be able to ban a user')

    def test_officer_can_leave(self):
        self.group_tester.make_officer(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.leave', self.club):
            self.fail('Officer should be able to leave a club')

    def test_officer_can_create_tournament(self):
        self.group_tester.make_officer(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.create_tournament', self.club):
            self.fail('Officer should be able to create tournament')

    def test_officer_can_apply_tournament(self):
        self.group_tester.make_officer(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.join_tournament', self.club):
            self.fail('Officer should be able to apply to a tournament')

    def test_owner_can_access_club_info(self):
        if not self.owner.has_club_perm('chessclubs.access_club_info', self.club):
            self.fail('Owner should have access to club info')

    def test_owner_can_access_club_owner_public_info(self):
        if not self.club.owner.has_club_perm('chessclubs.access_club_owner_public_info', self.club):
            self.fail('Owner should have access to cub owner public info')

    def test_owner_can_manage_applications(self):
        if not self.club.owner.has_club_perm('chessclubs.manage_applications', self.club):
            self.fail('Owner should be able to manage applications')

    def test_owner_can_access_members_list(self):
        if not self.club.owner.has_club_perm('chessclubs.access_members_list', self.club):
            self.fail('Owner should have access to members list')

    def test_owner_can_access_public_info(self):
        if not self.club.owner.has_club_perm('chessclubs.show_public_info', self.club):
            self.fail('Owner should have access to public info')

    def test_owner_can_access_private_info(self):
        if not self.club.owner.has_club_perm('chessclubs.show_private_info', self.club):
            self.fail('Owner should have access to private info')

    def test_owner_can_promote_members(self):
        if not self.club.owner.has_club_perm('chessclubs.promote', self.club):
            self.fail('Owner should be able to promote members')

    def test_owner_can_demote_officers(self):
        if not self.club.owner.has_club_perm('chessclubs.demote', self.club):
            self.fail('Owner should be able to demote officers')

    def test_owner_can_transfer_ownership(self):
        if not self.club.owner.has_club_perm('chessclubs.transfer_ownership', self.club):
            self.fail('Owner should be able to transfer_ownership')

    def test_owner_cannot_apply_to_club(self):
        if self.owner.has_club_perm('chessclubs.apply_to_club', self.club):
            self.fail('Officer should not be able to apply to club')

    def test_owner_cannot_acknowledge_application_response(self):
        if self.owner.has_club_perm('chessclubs.acknowledge_response', self.club):
            self.fail('Owner should not be able to acknowledge response')

    def test_owner_can_ban(self):
        if not self.owner.has_club_perm('chessclubs.ban', self.club):
            self.fail('Owner should not be able to ban a user')

    def test_owner_cannot_leave(self):
        if self.owner.has_club_perm('chessclubs.leave', self.club):
            self.fail('Owner should be able to leave a club')

    def test_owner_can_create_tournament(self):
        if not self.owner.has_club_perm('chessclubs.create_tournament', self.club):
            self.fail('Owner should be able to create tournament')

    def test_owner_can_apply_tournament(self):
        if not self.owner.has_club_perm('chessclubs.join_tournament', self.club):
            self.fail('Owner should be able to apply to a tournament')

    def test_denied_applicant_can_access_club_info(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_info', self.club):
            self.fail('Owner applicant should have access to club info')

    def test_denied_applicant_can_access_club_owner_public_info(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_owner_public_info', self.club):
            self.fail('Denied applicant should have access to cub owner public info')

    def test_denied_applicant_cannot_manage_applications(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.manage_applications', self.club):
            self.fail('Denied applicant should not be able to manage applications')

    def test_denied_applicant_cannot_access_members_list(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.access_members_list', self.club):
            self.fail('Denied applicant should not have access to members list')

    def test_denied_applicant_cannot_access_public_info(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.show_public_info', self.club):
            self.fail('Denied applicant should not have access to public info')

    def test_denied_applicant_cannot_access_private_info(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.show_private_info', self.club):
            self.fail('Denied applicant should not have access to private info')

    def test_denied_applicant_cannot_promote_members(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.promote', self.club):
            self.fail('Denied applicant should not be able to promote members')

    def test_denied_applicant_cannot_demote_officers(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.demote', self.club):
            self.fail('Denied applicant should not be able to demote officers')

    def test_denied_applicant_cannot_transfer_ownership(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.transfer_ownership', self.club):
            self.fail('Denied applicant should not be able to transfer_ownership')

    def test_denied_applicant_cannot_apply_to_club(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.apply_to_club', self.club):
            self.fail('Denied applicant should not be able to apply to club')

    def test_denied_applicant_can_acknowledge_application_response(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.acknowledge_response', self.club):
            self.fail('Denied applicant should be able to acknowledge response')

    def test_denied_applicant_cannot_ban(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.ban', self.club):
            self.fail('Denied applicant should not be able to ban a user')

    def test_denied_applicant_cannot_leave(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.leave', self.club):
            self.fail('Denied applicant should not be able to leave a club')

    def test_denied_applicant_cannot_create_tournament(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.create_tournament', self.club):
            self.fail('Denied applicant should not be able to create tournament')

    def test_denied_applicant_cannot_apply_tournament(self):
        self.group_tester.make_denied_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.join_tournament', self.club):
            self.fail('Denied Applicant should not be able to apply to a tournament')

    def test_accepted_applicant_can_access_club_info(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_info', self.club):
            self.fail('Accepted applicant should have access to club info')

    def test_accepted_applicant_can_access_club_owner_public_info(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_owner_public_info', self.club):
            self.fail('Accepted applicant should have access to cub owner public info')

    def test_accepted_applicant_cannot_manage_applications(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.manage_applications', self.club):
            self.fail('Accepted applicant should not be able to manage applications')

    def test_accepted_applicant_cannot_access_members_list(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.access_members_list', self.club):
            self.fail('Accepted applicant should not have access to members list')

    def test_accepted_applicant_cannot_access_public_info(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.show_public_info', self.club):
            self.fail('Accepted applicant should not have access to public info')

    def test_accepted_applicant_cannot_access_private_info(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.show_private_info', self.club):
            self.fail('Accepted applicant should not have access to private info')

    def test_accepted_applicant_cannot_promote_members(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.promote', self.club):
            self.fail('Accepted applicant should not be able to promote members')

    def test_accepted_applicant_cannot_demote_officers(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.demote', self.club):
            self.fail('Accepted applicant should not be able to demote officers')

    def test_accepted_applicant_cannot_transfer_ownership(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.transfer_ownership', self.club):
            self.fail('Accepted applicant should not be able to transfer_ownership')

    def test_accepted_applicant_cannot_apply_to_club(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.apply_to_club', self.club):
            self.fail('Accepted applicant should not be able to apply to club')

    def test_accepted_applicant_cannot_ban(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.ban', self.club):
            self.fail('Accepted applicant should not be able to ban a user')

    def test_accepted_applicant_cannot_leave(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.leave', self.club):
            self.fail('Accepted applicant should not be able to leave a club')

    def test_accepted_applicant_cannot_create_tournament(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.create_tournament', self.club):
            self.fail('Accepted applicant should not be able to create tournament')

    def test_accepted_applicant_can_acknowledge_application_response(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.acknowledge_response', self.club):
            self.fail('Accepted applicant should be able to acknowledge response')

    def test_accepted_applicant_cannot_apply_tournament(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        if self.other_user.has_club_perm('chessclubs.join_tournament', self.club):
            self.fail('Accepted applicant should not be able to apply to a tournament')

    def test_logged_in_non_member_can_access_club_info(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_info', self.club):
            self.fail('Logged-in non-member should have access to club info')

    def test_logged_in_non_member_can_access_club_owner_public_info(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.access_club_owner_public_info', self.club):
            self.fail('Logged-in non-member should have access to cub owner public info')

    def test_logged_in_non_member_cannot_manage_applications(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.manage_applications', self.club):
            self.fail('Logged-in non-member should not be able to manage applications')

    def test_logged_in_non_member_cannot_access_members_list(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.access_members_list', self.club):
            self.fail('Logged-in non-member should not have access to members list')

    def test_logged_in_non_member_cannot_access_public_info(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.show_public_info', self.club):
            self.fail('Logged-in non-member should not have access to public info')

    def test_logged_in_non_member_cannot_access_private_info(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.show_private_info', self.club):
            self.fail('Logged-in non-member should not have access to private info')

    def test_logged_in_non_member_cannot_promote_members(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.promote', self.club):
            self.fail('Logged-in non-member should not be able to promote members')

    def test_logged_in_non_member_cannot_demote_officers(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.demote', self.club):
            self.fail('Logged-in non-member should not be able to demote officers')

    def test_logged_in_non_member_cannot_transfer_ownership(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.transfer_ownership', self.club):
            self.fail('Logged-in non-member should not be able to transfer_ownership')

    def test_logged_in_non_member_can_apply_to_club(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if not self.other_user.has_club_perm('chessclubs.apply_to_club', self.club):
            self.fail('Logged-in non-member should not be able to apply to club')

    def test_logged_in_non_member_cannot_acknowledge_application_response(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.acknowledge_response', self.club):
            self.fail('Logged-in non-member should be able to acknowledge response')

    def test_logged_in_non_member_cannot_ban(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.ban', self.club):
            self.fail('Logged-in non-member should not be able to ban a user')

    def test_logged_in_non_member_cannot_leave(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.leave', self.club):
            self.fail('Logged-in non-member should not be able to leave a club')

    def test_logged_in_non_member_cannot_create_tournament(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.create_tournament', self.club):
            self.fail('Logged-in non-member should not be able to create tournament')

    def test_logged_in_non_member_cannot_apply_tournament(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        if self.other_user.has_club_perm('chessclubs.join_tournament', self.club):
            self.fail('Logged-in non-member should not be able to apply to a tournament')
