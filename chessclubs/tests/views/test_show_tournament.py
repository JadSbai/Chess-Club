from django.contrib import messages

from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN

class ShowTournamentViewTestCase(TestCase):

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json'
                ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.user2 = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.group_tester = ClubGroupTester(self.club)
        self.group_tester.make_officer(self.user2)
        self.client.login(email=self.user.email, password='Password123')
        self.url = reverse('show_tournament', kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name})
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)


    def test_view_show_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/')

    # def test_see_wrong_tournament(self):
    #     bad_url = reverse('show_tournament',  kwargs={'club_name': self.club.name, 'tournament_name': "ops"})
    #     response = self.client.get(bad_url, follow=True)
    #     target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
    #     self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
    #     messages_list = list(response.context['messages'])
    #     self.assertEqual(len(messages_list), 1)
    #     self.assertEqual(messages_list[0].level, messages.ERROR)
    #     self.assertEqual(messages_list[0].message, "The tournament you are looking for does not exist!")

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in',reverse('show_tournament', kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_can_see_tournament_page(self):
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester.make_member(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_officer_can_see_tournament_page(self):
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester.make_officer(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_owner_can_see_tournament_page(self):
        self.client.login(email=self.club.owner.email, password='Password123')
        self.group_tester.make_officer(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_applicant_can_see_tournament_page(self):
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester.make_applicant(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_accepted_applicant_can_see_tournament_page(self):
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester.make_accepted_applicant(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_denied_applicant_can_see_tournament_page(self):
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester.make_denied_applicant(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_logged_in_non_members_can_see_tournament_page(self):
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester.make_authenticated_non_member(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
