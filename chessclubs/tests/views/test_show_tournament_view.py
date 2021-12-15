from django.contrib import messages

from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next, TournamentGroupTester
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
    @classmethod
    def setUpTestData(cls):
        cls.organiser = User.objects.get(email='johndoe@example.org')
        cls.co_organiser = User.objects.get(email='janedoe@example.org')
        cls.member = User.objects.get(email='petrapickles@example.org')
        cls.other_user = User.objects.get(email='peterpickles@example.org')
        cls.club = Club.objects.get(name="Test_Club")
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.group_tester = ClubGroupTester(cls.club)
        cls.tournament_tester = TournamentGroupTester(cls.tournament)
        cls.group_tester.make_officer(cls.co_organiser)
        cls.group_tester.make_member(cls.member)
        cls.url = reverse('show_tournament', kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_view_show_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/')

    def test_see_wrong_tournament(self):
        bad_url = reverse('show_tournament',  kwargs={'club_name': self.club.name, 'tournament_name': "oops"})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The tournament you are looking for does not exist!")

    def test_wrong_club_show_tournament(self):
        bad_url = reverse('transfer_ownership', kwargs={'club_name': "blabla", 'tournament_name': self.tournament.name})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_page_content_when_not_finished_deadline_passed_enough_players_published_as_organiser(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_published_as_co_organiser(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_published_as_participant(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_published_as_non_participant(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_published_as_organiser(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_published_as_co_organiser(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_published_as_participant(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_published_as_non_participant(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_as_organiser(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_as_co_organiser(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_as_participant(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_as_non_participant(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_not_enough_players_as_organiser(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_not_enough_players_as_co_organiser(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_not_enough_players_as_participant(self):
        pass

    def test_page_content_when_not_finished_deadline_passed_not_enough_players_as_non_participant(self):
        pass

    def test_page_content_when_not_finished_not_deadline_passed_as_organiser(self):
        pass

    def test_page_content_when_not_finished_not_deadline_passed_as_co_organiser(self):
        pass

    def test_page_content_when_not_finished_not_deadline_passed_as_participant(self):
        pass

    def test_page_content_when_not_finished_not_deadline_passed_as_non_participant(self):
        pass

    def test_page_content_when_finished_as_organiser(self):
        pass

    def test_page_content_when_finished_as_co_organiser(self):
        pass

    def test_page_content_when_finished_as_participant(self):
        pass

    def test_page_content_when_finished_as_non_participant(self):
        pass

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
        #self.group_tester.make_officer(self.user)
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

    def _assert_response_redirect(self, response):
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_valid_response(self, response):
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
