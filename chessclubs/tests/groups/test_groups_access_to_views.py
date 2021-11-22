"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User
from django.urls import reverse
from chessclubs.tests.helpers import GroupTester


class ShowUserViewRestrictedAccessTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.client.login(email=self.user.email, password='Password123')
        self.target_user = User.objects.get(email='janedoe@example.org')
        self.group_tester = GroupTester()

    def test_applicant_cannot_access_show_user(self):
        self.group_tester.make_applicant(self.user)
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_applicant_cannot_access_members_list(self):
        self.group_tester.make_applicant(self.user)
        self.url = reverse('user_list')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_applicant_cannot_promote_members(self):
        self.group_tester.make_applicant(self.user)
        self.group_tester.make_member(self.target_user)
        self.url = reverse('promote', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_applicant_cannot_demote_officers(self):
        self.group_tester.make_applicant(self.user)
        self.url = reverse('demote', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_applicant_cannot_transfer_ownership(self):
        self.group_tester.make_applicant(self.user)
        self.url = reverse('transfer_ownership', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_member_can_access_members_list(self):
        self.group_tester.make_member(self.user)
        self.url = reverse('user_list')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_member_can_access_show_user(self):
        self.group_tester.make_member(self.user)
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_member_cannot_promote_members(self):
        self.group_tester.make_member(self.user)
        self.group_tester.make_member(self.target_user)
        self.url = reverse('promote', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_member_cannot_demote_officers(self):
        self.group_tester.make_member(self.user)
        self.group_tester.make_officer(self.target_user)
        self.url = reverse('demote', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_member_cannot_transfer_ownership(self):
        self.group_tester.make_member(self.user)
        self.group_tester.make_officer(self.target_user)
        self.url = reverse('transfer_ownership', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_officer_can_access_members_list(self):
        self.group_tester.make_officer(self.user)
        self.url = reverse('user_list')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_officer_can_access_show_user(self):
        self.group_tester.make_officer(self.user)
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_officer_cannot_promote_members(self):
        self.group_tester.make_officer(self.user)
        self.group_tester.make_member(self.target_user)
        self.url = reverse('promote', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_officer_cannot_demote_officers(self):
        self.group_tester.make_officer(self.user)
        self.group_tester.make_officer(self.target_user)
        self.url = reverse('demote', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_officer_cannot_transfer_ownership(self):
        self.group_tester.make_officer(self.user)
        self.group_tester.make_officer(self.target_user)
        self.url = reverse('transfer_ownership', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_owner_can_access_members_list(self):
        self.group_tester.make_owner(self.user)
        self.url = reverse('user_list')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_owner_can_access_show_user(self):
        self.group_tester.make_owner(self.user)
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_owner_can_promote_member(self):
        self.group_tester.make_owner(self.user)
        self.url = reverse('promote', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_owner_can_demote(self):
        self.group_tester.make_owner(self.user)
        self.url = reverse('demote', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_owner_can_transfer_ownership(self):
        self.group_tester.make_owner(self.user)
        self.url = reverse('transfer_ownership', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
