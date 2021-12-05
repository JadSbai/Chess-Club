from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import reverse_with_next, ClubGroupTester


class UserListTest(TestCase):

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/default_club.json',
                ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.url = reverse('user_list', kwargs={'club_name': self.club.name})


    def test_user_list_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/users/')

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
