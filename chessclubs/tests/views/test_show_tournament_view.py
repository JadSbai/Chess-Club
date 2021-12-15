from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next, TournamentGroupTester, _create_test_players


class ShowTournamentViewTestCase(TestCase, AssertHTMLMixin):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json'
                ]

    @classmethod
    def setUpTestData(cls):
        cls.organiser = User.objects.get(email='johndoe@example.org')
        cls.co_organiser = User.objects.get(email='janedoe@example.org')
        cls.participant = User.objects.get(email='petrapickles@example.org')
        cls.non_participant = User.objects.get(email='peterpickles@example.org')
        cls.any_user = User.objects.get(email='morganezadjlic@example.org')
        cls.club = Club.objects.get(name="Test_Club")
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.club_tester = ClubGroupTester(cls.club)
        cls.tournament_tester = TournamentGroupTester(cls.tournament)
        cls.club_tester.make_officer(cls.co_organiser)
        cls.tournament_tester.make_co_organiser(cls.co_organiser)
        cls.club_tester.make_member(cls.participant)
        cls.tournament_tester.make_participant(cls.participant)
        cls.club_tester.make_member(cls.non_participant)
        _create_test_players(10, cls.club, cls.tournament)
        cls.url = reverse('show_tournament',
                          kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        cls.show_schedule_url = reverse('show_schedule',
                                        kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.publish_schedule_url = reverse('publish_schedule',
                                           kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.start_tournament_url = reverse('start_tournament',
                                           kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.create_tournament_url = reverse('create_tournament', kwargs={'club_name': cls.club.name})

    def test_view_show_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/')

    def test_see_wrong_tournament(self):
        self.client.login(email=self.organiser.email, password='Password123')
        bad_url = reverse('show_tournament', kwargs={'club_name': self.club.name, 'tournament_name': "oops"})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('show_club', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The tournament you are looking for does not exist!")

    def test_wrong_club_show_tournament(self):
        self.client.login(email=self.organiser.email, password='Password123')
        bad_url = reverse('show_tournament', kwargs={'club_name': "blabla", 'tournament_name': self.tournament.name})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_page_content_when_not_finished_deadline_passed_enough_players_published_as_organiser(self):
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        self.client.login(email=self.organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_show_schedule(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_published_as_co_organiser(self):
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        self.client.login(email=self.co_organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_show_schedule(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_published_as_participant(self):
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        self.client.login(email=self.participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_show_schedule(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_published_as_non_participant(self):
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        self.client.login(email=self.non_participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_show_schedule(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_published_as_organiser(self):
        self.tournament._set_deadline_now()
        self.client.login(email=self.organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_publish_schedule(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_published_as_co_organiser(self):
        self.tournament._set_deadline_now()
        self.client.login(email=self.co_organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_publish_schedule(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_published_as_participant(self):
        self.tournament._set_deadline_now()
        self.client.login(email=self.participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_publish_schedule(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_published_as_non_participant(self):
        self.tournament._set_deadline_now()
        self.client.login(email=self.non_participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_publish_schedule(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_published_as_organiser(self):
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        self.client.login(email=self.organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_start_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_published_as_co_organiser(self):
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        self.client.login(email=self.co_organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_start_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_published_as_participant(self):
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        self.client.login(email=self.participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_start_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_published_as_non_participant(
            self):
        self.tournament._set_deadline_now()
        self.tournament.publish_schedule()
        self.client.login(email=self.non_participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_start_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_not_published_as_organiser(self):
        self.tournament._set_deadline_now()
        self.client.login(email=self.organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_start_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_not_published_as_co_organiser(
            self):
        self.tournament._set_deadline_now()
        self.client.login(email=self.co_organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_start_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_not_published_as_participant(
            self):
        self.tournament._set_deadline_now()
        self.client.login(email=self.participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_start_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_enough_players_not_started_not_published_as_non_participant(
            self):
        self.tournament._set_deadline_now()
        self.client.login(email=self.non_participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_start_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_not_enough_players_as_organiser(self):
        self.tournament._remove_all_participants()
        self.tournament._set_deadline_now()
        self.client.login(email=self.organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_create_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_not_enough_players_as_co_organiser(self):
        self.tournament._remove_all_participants()
        self.tournament._set_deadline_now()
        self.client.login(email=self.co_organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_create_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_not_enough_players_as_participant(self):
        self.tournament._remove_all_participants()
        self.tournament._set_deadline_now()
        self.client.login(email=self.participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_create_tournament(response)

    def test_page_content_when_not_finished_deadline_passed_not_enough_players_as_non_participant(self):
        self.tournament._remove_all_participants()
        self.tournament._set_deadline_now()
        self.client.login(email=self.non_participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_not_create_tournament(response)

    def test_page_content_when_not_finished_not_deadline_passed_as_organiser(self):
        self.client.login(email=self.organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_no_button_appears(response)

    def test_page_content_when_not_finished_not_deadline_passed_as_co_organiser(self):
        self.client.login(email=self.co_organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_no_button_appears(response)

    def test_page_content_when_not_finished_not_deadline_passed_as_participant(self):
        self.client.login(email=self.participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_no_button_appears(response)

    def test_page_content_when_not_finished_not_deadline_passed_as_non_participant(self):
        self.client.login(email=self.non_participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_no_button_appears(response)

    def test_page_content_when_finished_as_organiser(self):
        self.tournament._set_finished()
        self.client.login(email=self.organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_winner_is_showed(response)
        self._assert_no_button_appears(response)

    def test_page_content_when_finished_as_co_organiser(self):
        self.tournament._set_finished()
        self.client.login(email=self.co_organiser.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_winner_is_showed(response)
        self._assert_no_button_appears(response)

    def test_page_content_when_finished_as_participant(self):
        self.tournament._set_finished()
        self.client.login(email=self.participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_winner_is_showed(response)
        self._assert_no_button_appears(response)

    def test_page_content_when_finished_as_non_participant(self):
        self.tournament._set_finished()
        self.client.login(email=self.non_participant.email, password='Password123')
        response = self.client.get(self.url)
        self._assert_winner_is_showed(response)
        self._assert_no_button_appears(response)

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('show_tournament', kwargs={'club_name': self.club.name,
                                                                                      'tournament_name': self.tournament.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_member_can_see_tournament_page(self):
        self.client.login(email=self.any_user.email, password='Password123')
        self.club_tester.make_member(self.any_user)
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_officer_can_see_tournament_page(self):
        self.client.login(email=self.any_user.email, password='Password123')
        self.club_tester.make_officer(self.any_user)
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_owner_can_see_tournament_page(self):
        self.client.login(email=self.club.owner.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_applicant_can_see_tournament_page(self):
        self.client.login(email=self.any_user.email, password='Password123')
        self.club_tester.make_applicant(self.any_user)
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_accepted_applicant_can_see_tournament_page(self):
        self.client.login(email=self.any_user.email, password='Password123')
        self.club_tester.make_accepted_applicant(self.any_user)
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_denied_applicant_can_see_tournament_page(self):
        self.client.login(email=self.any_user.email, password='Password123')
        self.club_tester.make_denied_applicant(self.any_user)
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_logged_in_non_members_can_see_tournament_page(self):
        self.client.login(email=self.any_user.email, password='Password123')
        self.club_tester.make_authenticated_non_member(self.any_user)
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def _assert_response_redirect(self, response):
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_valid_response(self, response):
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def _assert_show_schedule(self, response):
        self.assertContains(response, f"{self.show_schedule_url}")
        with self.assertHTML(response) as html:
            button = html.find(f'.//div/a[@href="{self.show_schedule_url}"]')
            self.assertIsNotNone(button)

    def _assert_not_show_schedule(self, response):
        self.assertNotContains(response, f"{self.show_schedule_url}")
        with self.assertHTML(response) as html:
            button = html.find(f'.//div/a[@href="{self.show_schedule_url}"]')
            self.assertIsNone(button)

    def _assert_publish_schedule(self, response):
        self.assertContains(response, f"{self.publish_schedule_url}")
        with self.assertHTML(response) as html:
            button = html.find(f'.//div/a[@href="{self.publish_schedule_url}"]')
            self.assertIsNotNone(button)

    def _assert_not_publish_schedule(self, response):
        self.assertNotContains(response, f"{self.publish_schedule_url}")
        with self.assertHTML(response) as html:
            button = html.find(f'.//div/a[@href="{self.publish_schedule_url}"]')
            self.assertIsNone(button)

    def _assert_start_tournament(self, response):
        self.assertContains(response, f"{self.start_tournament_url}")
        with self.assertHTML(response) as html:
            button = html.find(f'.//div/a[@href="{self.start_tournament_url}"]')
            self.assertIsNotNone(button)

    def _assert_not_start_tournament(self, response):
        self.assertNotContains(response, f"{self.start_tournament_url}")
        with self.assertHTML(response) as html:
            button = html.find(f'.//div/a[@href="{self.start_tournament_url}"]')
            self.assertIsNone(button)

    def _assert_create_tournament(self, response):
        self.assertContains(response, f"{self.create_tournament_url}")
        with self.assertHTML(response) as html:
            button = html.find(f'.//div/a[@href="{self.create_tournament_url}"]')
            self.assertIsNotNone(button)

    def _assert_not_create_tournament(self, response):
        self.assertNotContains(response, f"{self.create_tournament_url}")
        with self.assertHTML(response) as html:
            button = html.find(f'.//div/a[@href="{self.create_tournament_url}"]')
            self.assertIsNone(button)

    def _assert_no_button_appears(self, response):
        self._assert_not_create_tournament(response)
        self._assert_not_show_schedule(response)
        self._assert_not_publish_schedule(response)
        self._assert_not_start_tournament(response)

    def _assert_winner_is_showed(self, response):
        self.assertContains(response, f"{self.tournament.get_winner()}")
        with self.assertHTML(response) as html:
            paragraph = html.find(f'.//div/p[@id="winner"]')
            self.assertTrue(f"{self.tournament.get_winner()}")
            self.assertIsNotNone(paragraph)
