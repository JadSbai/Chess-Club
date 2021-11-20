"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from chessclubs.models import User
from django.contrib.auth.models import Group
from django.urls import reverse
from chessclubs.groups import members_permissions, officers_permissions, owner_permissions, members, officers, applicants


class ShowUserViewRestrictedAccessTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.client.login(email=self.user.email, password='Password123')
        self.applicants, created = Group.objects.get_or_create(name="applicants")
        self.members, created2 = Group.objects.get_or_create(name="members")
        self.officers, created3 = Group.objects.get_or_create(name="officers")
        self.target_user = User.objects.get(email='janedoe@example.org')


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

    def test_applicant_cannot_access_show_user(self):
        self.makeApplicant()
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_applicant_cannot_access_members_list(self):
        self.makeApplicant()
        self.url = reverse('user_list')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_member_can_access_members_list(self):
        self.makeMember()
        self.url = reverse('user_list')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_member_can_access_show_user(self):
        self.makeMember()
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_officer_can_access_members_list(self):
        self.makeOfficer()
        self.url = reverse('user_list')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_officer_can_access_show_user(self):
        self.makeOfficer()
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_owner_can_access_members_list(self):
        self.makeOwner()
        self.url = reverse('user_list')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_owner_can_access_show_user(self):
        self.makeOwner()
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)


