from django.contrib import messages

from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next, TournamentGroupTester
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN

class ApplyTournamentViewTestCase(TestCase):

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json'
                ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.member = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        #self.group_tester.make_officer(self.user2)
        self.tournament = Tournament.objects.get(name="Test_Tournament")
        self.tournament_tester = TournamentGroupTester(self.tournament)
        self.client.login(email=self.member.email, password='Password123')
        self.url = reverse('apply_tournament', kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name})
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)


    def test_view_apply_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/apply/')

    def test_members_can_apply(self):
        self.group_tester.make_member(self.member)
        #self.tournament_tester.make_participant(self.user2)
        response = self.client.get(self.url, follow=True)
        self.assertTrue(self.tournament.is_participant(self.member))

    def test_organiser_cannot_apply(self):
        self.client.login(email=self.user.email, password='Password123')
        self.tournament_tester.make_organiser(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertFalse(self.tournament.is_participant(self.user))

    # def test_co_organiser_cannot_apply(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     self.tournament_tester.make_organiser(self.user)
    #     response = self.client.get(self.url, follow=True)
    #     self.assertFalse(self.tournament.is_participant(self.user))

    # def test_authinticated_non_members_cannot_apply(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     self.group_tester.make_authenticated_non_member(self.user)
    #     response = self.client.get(self.url, follow=True)
    #     self.assertFalse(self.tournament.is_participant(self.user))

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in',reverse('apply_tournament', kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_officer_can_apply(self):
        self.group_tester.make_officer(self.member)
        response = self.client.get(self.url, follow=True)
        self.assertTrue(self.tournament.is_participant(self.member))

    def test_owner_can_apply(self):
        self.client.login(email=self.club.owner.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertTrue(self.tournament.is_participant(self.club.owner))
