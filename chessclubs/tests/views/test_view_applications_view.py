from chessclubs.models import User, Club
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from django.test import TestCase
from django.urls import reverse

class ApplicationViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json'
                ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.user2 = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_officer(self.user2)
        self.client.login(email=self.user2.email, password='Password123')
        self.url = reverse('view_applications', kwargs={'club_name': self.club.name})

    def test_view_application_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/view_applications/')

    def test_get_applicants_list(self):
        self._create_test_users(15)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assertEqual(len(response.context['applicants']), 15)
        for user_id in range(15-1):
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            user = User.objects.get(email=f'user{user_id}@test.org')
            user_url = reverse('show_user', kwargs={'user_id': user.id, 'club_name': self.club.name})
            self.assertContains(response, user_url)

    def test_get_user_list_redirects_when_not_logged_in(self):
        self.client.logout()
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
            self.club.add_to_applicants_group(user)
