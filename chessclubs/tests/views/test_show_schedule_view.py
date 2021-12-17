"""Tests of the show schedule view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, TournamentGroupTester, reverse_with_next, _create_test_players, \
    enter_results_to_all_matches
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from with_asserts.mixin import AssertHTMLMixin


class ShowTournamentScheduleTestCase(TestCase, AssertHTMLMixin):
    """Tests of the show_schedule view."""

    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                ]

    @classmethod
    def setUpTestData(cls):
        cls.club = Club.objects.get(name="Test_Club")
        cls.organiser = User.objects.get(email='johndoe@example.org')  # also tournament organiser
        cls.participant = User.objects.get(email='janedoe@example.org')
        cls.non_participant = User.objects.get(email="petrapickles@example.org")
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.tournament._set_deadline_now()
        cls.group_tester = ClubGroupTester(cls.club)
        cls.group_tester.make_member(cls.non_participant)
        cls.tournament_tester = TournamentGroupTester(cls.tournament)
        _create_test_players(95, cls.club, cls.tournament)
        cls.url = reverse('show_schedule',
                          kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.show_tournament_url = reverse('show_tournament',
                                          kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def setUp(self):
        self.group_tester.make_member(self.participant)
        self.tournament_tester.make_participant(self.participant)
        self.client.login(email=self.participant.email, password='Password123')

    def test_show_schedule_of_tournament_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/show_schedule/')

    def test_can_show_schedule_if_published_and_not_finished(self):
        self.tournament.publish_schedule()
        response1 = self.client.get(self.url, follow=True)
        self.assertEqual(response1.status_code, 200)
        self.assert_correct_large_pool_phase_display(response1)
        enter_results_to_all_matches(self.tournament)
        response2 = self.client.get(self.url, follow=True)
        for pool in self.tournament.get_current_pool_phase().get_pools():
            self.assertEqual(pool.get_players_count(), 4)
        self.assertEqual(response2.status_code, 200)
        self.assert_correct_small_pool_phase_display(response2)
        enter_results_to_all_matches(self.tournament)
        response3 = self.client.get(self.url, follow=True)
        self.assertEqual(response3.status_code, 200)
        self.assert_correct_eighth_final_display(response3)
        enter_results_to_all_matches(self.tournament)
        response4 = self.client.get(self.url, follow=True)
        self.assertEqual(response4.status_code, 200)
        self.assert_correct_quarter_final_display(response4)
        enter_results_to_all_matches(self.tournament)
        response5 = self.client.get(self.url, follow=True)
        self.assertEqual(response5.status_code, 200)
        self.assert_correct_semi_final_display(response5)
        enter_results_to_all_matches(self.tournament)
        response6 = self.client.get(self.url, follow=True)
        self.assertEqual(response6.status_code, 200)
        self.assert_correct_final_display(response6)
        enter_results_to_all_matches(self.tournament)
        response6 = self.client.get(self.url, follow=True)
        self.assertEqual(response6.status_code, 200)
        self._assert_response_redirect(response6, self.show_tournament_url)

    def test_cannot_show_schedule_if_not_published(self):
        self._assert_invalid_show_schedule()

    def test_organiser_can_see_schedule(self):
        self.client.logout()
        self.client.login(email=self.organiser.email, password='Password123')
        self.tournament.publish_schedule()
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_co_organiser_can_see_schedule(self):
        self.tournament.publish_schedule()
        self.tournament_tester.make_co_organiser(self.participant)
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_participant_can_see_schedule(self):
        self.tournament.publish_schedule()
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_non_participant_cannot_see_schedule(self):
        self.tournament.publish_schedule()
        self.client.logout()
        self.client.login(email=self.non_participant.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response, self.show_tournament_url)

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('show_schedule',
                                                           kwargs={'club_name': self.club.name,
                                                                   'tournament_name': self.tournament.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_see_schedule_of_wrong_tournament(self):
        self.tournament.publish_schedule()
        bad_url = reverse('show_schedule', kwargs={'club_name': self.club.name, 'tournament_name': "oops"})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('show_club', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The tournament you are looking for does not exist!")

    def test_wrong_club_see_schedule_from_tournament(self):
        self.tournament.publish_schedule()
        bad_url = reverse('show_schedule', kwargs={'club_name': "blabla", 'tournament_name': self.tournament.name})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def _assert_invalid_show_schedule(self):
        before = self.tournament.get_participant_count()
        response = self.client.get(self.url, follow=True)
        after = self.tournament.get_participant_count()
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        self.assertEqual(before, after)
        self.assertTrue(self.tournament.is_participant(self.participant))
        self.assertTrue(self.tournament.user_status(self.participant), "participant")
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_response_redirect(self, response, url):
        self.assertRedirects(response, url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_valid_response(self, response):
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        for message in messages_list:
            self.assertNotEqual(message.level, messages.WARNING)

    def assert_correct_large_pool_phase_display(self, response):
        with self.assertHTML(response) as html:
            pool_phase = html.find(f'.//h3[@id="pool_phase"]')
            self.assertEqual(pool_phase.text, "Large-Pool-Phase")
        with self.assertHTML(response, selector='.pool') as pools:
            self.assertEqual(len(pools), 16)
            for i in range(1, 17):
                self.assertContains(response, f"Pool {i}")
        with self.assertHTML(response, '.enter_match_result') as elems:
            self.assertEqual(240, len(elems))
            self.assert_pool_phase_type_enter_result(elems)

    def assert_correct_small_pool_phase_display(self, response):
        with self.assertHTML(response) as html:
            pool_phase = html.find(f'.//h3[@id="pool_phase"]')
            self.assertEqual(pool_phase.text, "Small-Pool-Phase")
        with self.assertHTML(response, '.pool') as pools:
            self.assertEqual(len(pools), 8)
            for i in range(1, 9):
                self.assertContains(response, f"Pool {i}")
        with self.assertHTML(response, '.enter_match_result') as elems:
            self.assertEqual(48, len(elems))
            self.assert_pool_phase_type_enter_result(elems)

    def assert_pool_phase_type_enter_result(self, elements):
        for elem in elements:
            player1 = elem.find(f'a[@id="player1_winner"]')
            player2 = elem.find(f'a[@id="player2_winner"]')
            draw = elem.find(f'a[@id="draw"]')
            self.assertIsNotNone(player1)
            self.assertIsNotNone(player2)
            self.assertIsNotNone(draw)

    def assert_elimination_type_enter_result(self, elements):
        for elem in elements:
            player1 = elem.find(f'a[@id="player1_loser"]')
            player2 = elem.find(f'a[@id="player2_loser"]')
            self.assertIsNotNone(player1)
            self.assertIsNotNone(player2)

    def assert_correct_eighth_final_display(self, response):
        with self.assertHTML(response) as html:
            pool_phase = html.find(f'.//h3[@id="elimination_phase"]')
            self.assertEqual(pool_phase.text, "Eighth-Final")
        with self.assertHTML(response, '.enter_match_winner') as elems:
            self.assertEqual(8, len(elems))
            self.assert_elimination_type_enter_result(elems)

    def assert_correct_quarter_final_display(self, response):
        with self.assertHTML(response) as html:
            pool_phase = html.find(f'.//h3[@id="elimination_phase"]')
            self.assertEqual(pool_phase.text, "Quarter-Final")
        with self.assertHTML(response, '.enter_match_winner') as elems:
            self.assertEqual(4, len(elems))
            self.assert_elimination_type_enter_result(elems)

    def assert_correct_semi_final_display(self, response):
        with self.assertHTML(response) as html:
            pool_phase = html.find(f'.//h3[@id="elimination_phase"]')
            self.assertEqual(pool_phase.text, "Semi-Final")
        with self.assertHTML(response, '.enter_match_winner') as elems:
            self.assertEqual(2, len(elems))
            self.assert_elimination_type_enter_result(elems)

    def assert_correct_final_display(self, response):
        with self.assertHTML(response) as html:
            pool_phase = html.find(f'.//h3[@id="elimination_phase"]')
            self.assertEqual(pool_phase.text, "Final")
        with self.assertHTML(response, '.enter_match_winner') as elems:
            self.assertEqual(1, len(elems))
            self.assert_elimination_type_enter_result(elems)


