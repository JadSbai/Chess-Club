from django.test import TestCase
from django.urls import reverse
from chessclubs.models import Club, User


class CreateClubTest(TestCase):
    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email='johndoe@example.org')
        self.url = reverse('create_club')
        self.data = {'name': 'y' * 40, 'description': 'x' * 200, 'location': 'z' * 20}

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_club/')

    def test_get_create_club_is_forbidden(self):
        self.client.login(email=self.user.email, password= 'Password123')
        club_count_before = Club.objects.count()
        response = self.client.get(self.url, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)


    def test_create_new_club_redirects_when_not_logged_in(self):
        club_count_before = Club.objects.count()
        redirect_url = reverse('log_in')
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)

    def test_successful_new_club(self):
        self.client.login(email=self.user.email, password="Password123")
        club_count_before = Club.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before + 1)
        new_club = Club.objects.last()
        self.assertEqual(self.user, new_club.owner)
        response_url = reverse('my_profile')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )


    def test_unsuccessful_new_club(self):
        self.client.login(email=self.user.email, password='Password123')
        club_count_before = Club.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)


    def test_cannot_create_club_for_other_user(self):
        self.client.login(email=self.user.email, password='Password123')
        other_user = User.objects.get(email='janedoe@example.org')
        self.data['owner'] = other_user.id
        club_count_before = Club.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before + 1)
        new_club = Club.objects.last()
        self.assertEqual(self.user, new_club.owner)