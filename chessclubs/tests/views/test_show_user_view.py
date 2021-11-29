from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import reverse_with_next, ClubGroupTester
from django.contrib.auth.models import Permission

class ShowUserTest(TestCase):

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.target_user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.club.add_member(self.target_user)
        self.club.members.add(self.user)
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_name': self.club.name})

    def test_show_user_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/user/{self.target_user.id}')

    def test_get_show_user_with_valid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "Jane Doe")

    def test_get_show_user_with_own_id(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id, 'club_name': self.club.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "John Doe")

    def test_get_show_user_with_invalid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id+9999, 'club_name': self.club.name})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_get_show_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)