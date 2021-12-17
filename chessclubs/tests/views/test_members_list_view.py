"""Tests of Members list view """
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from chessclubs.models import User, Club
from chessclubs.tests.helpers import reverse_with_next, ClubGroupTester



class MembersListTest(TestCase):
    """Tests of Members list view """

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.other_user = User.objects.get(email='petrapickles@example.org')
        self.group_tester = ClubGroupTester(self.club)
        self.url = reverse('user_list', kwargs={'club_name': self.club.name})
        self.redirect_url = reverse('show_club', kwargs={'club_name': self.club.name})


    def test_user_list_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/members/')

    def test_get_user_list(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_users(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), 15)
        for user_id in range(15-1):
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            self.assertContains(response, 'member')
            user = User.objects.get(email=f'user{user_id}@test.org')
            user_url = reverse('show_user', kwargs={'user_id': user.id, 'club_name': self.club.name})
            self.assertContains(response, user_url)

    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_user_in_wrong_club(self):
        self.client.login(email=self.user.email, password='Password123')
        bad_url = reverse('user_list', kwargs={'club_name': "blabla"})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing_page.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_applicant_cannot_access_the_members_list(self):
        self.group_tester.make_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_accepted_applicant_cannot_access_the_members_list(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_denied_applicant_cannot_access_the_members_list(self):
        self.group_tester.make_denied_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_member_can_access_the_members_list(self):
        self.group_tester.make_member(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_officer_can_access_the_members_list(self):
        self.group_tester.make_officer(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_owner_can_access_the_members_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_logged_in_non_member_cannot_access_the_user_page(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def _assert_response_redirect(self, response):
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_valid_response(self, response):
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def _create_test_users(self, user_count=10):
        for user_id in range(user_count):
            user = User.objects.create_user(
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
                chess_experience=f'Standard{user_id}',
                personal_statement=f'My name is {user_id}',
            )
            self.club.add_member(user)
