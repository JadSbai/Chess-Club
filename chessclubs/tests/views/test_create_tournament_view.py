from django.contrib import messages

from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from django.test import TestCase
from django.urls import reverse
from chessclubs.forms import TournamentForm
from django.utils import timezone
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN


class CreateTournamentViewTestCase(TestCase):
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
        self.url = reverse('create_tournament', kwargs={'club_name': self.club.name})
        self.data = {'name': 'y' * 40, 'location': 'x' * 40, 'description': 'Description', 'max_capacity': 20,
                     'deadline': (timezone.now() + timezone.timedelta(days=1))}
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_view_create_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/create_tournament/')

    def test_get_create_tournament(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_tournament.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TournamentForm))
        self.assertFalse(form.is_bound)

    def test_successful_new_tournament(self):
        self.client.login(email=self.user.email, password="Password123")
        tournament_count_before = Tournament.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()
        self.assertEqual(tournament_count_after, tournament_count_before + 1)
        new_tournament = Tournament.objects.last()
        self.assertEqual(self.user, new_tournament.organiser)
        response_url = reverse('show_tournament',
                               kwargs={'club_name': self.club.name, 'tournament_name': new_tournament.name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

    def test_unsuccessful_new_tournament(self):
        self.client.login(email=self.user.email, password='Password123')
        tournament_count_before = Tournament.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()
        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_tournament.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TournamentForm))
        self.assertTrue(form.is_bound)

    def test_wrong_club_create_tournament(self):
        bad_url = reverse('create_tournament', kwargs={'club_name': "blabla"})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('create_tournament', kwargs={'club_name': self.club.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_applicant_cannot_create_tournament(self):
        self.group_tester.make_applicant(self.user2)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_accepted_applicant_cannot_create_tournament(self):
        self.group_tester.make_accepted_applicant(self.user2)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_denied_applicant_cannot_create_tournament(self):
        self.group_tester.make_denied_applicant(self.user2)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_member_cannot_create_tournament(self):
        self.group_tester.make_member(self.user2)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_officer_can_create_tournament(self):
        self.group_tester.make_officer(self.user2)
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_owner_can_create_tournament(self):
        self.client.login(email=self.club.owner.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_logged_in_non_member_cannot_create_tournament(self):
        self.group_tester.make_authenticated_non_member(self.user2)
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
