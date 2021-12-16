"""Tests of enter result view"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club, Tournament, Match
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next, TournamentGroupTester, _create_test_players, \
    enter_results_to_all_matches
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages
from with_asserts.mixin import AssertHTMLMixin


class EnterResultViewTestCase(TestCase, AssertHTMLMixin):
    """Test Suites of my matches view"""
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/other_players.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                'chessclubs/tests/fixtures/other_clubs.json',
                'chessclubs/tests/fixtures/other_tournaments.json',
                'chessclubs/tests/fixtures/other_matches.json',
                ]

    @classmethod
    def setUpTestData(cls):
        cls.organiser = User.objects.get(email='johndoe@example.org')
        cls.co_organiser = User.objects.get(email='janedoe@example.org')
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.club = Club.objects.get(name="Test_Club")
        cls.random_member = User.objects.get(email="petrapickles@example.org")
        cls.participants = _create_test_players(17, cls.club, cls.tournament)
        cls.tournament._set_deadline_now()
        cls.tournament.start_tournament()
        cls.group_tester = ClubGroupTester(cls.club)
        cls.group_tester.make_member(cls.random_member)
        cls.tournament_tester = TournamentGroupTester(cls.tournament)
        cls.group_tester.make_officer(cls.co_organiser)
        cls.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        cls.show_tournament_url = reverse('show_tournament',
                                          kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.show_schedule_url = reverse('show_schedule',
                                          kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})

    def setUp(self):
        self.client.login(email=self.organiser.email, password='Password123')
        self.current_match = self.tournament.get_current_schedule()[0]
        self.player1_winner_url = reverse('enter_result',
                                         kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name,
                                                 'match_id': self.current_match.id, 'result': "player1"})
        self.player2_winner_url = reverse('enter_result',
                                         kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name,
                                                 'match_id': self.current_match.id, 'result': "player2"})
        self.draw_url = reverse('enter_result',
                               kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name,
                                       'match_id': self.current_match.id, 'result': "draw"})
        self.show_club_url = reverse('show_club', kwargs={'club_name': self.club.name})


    def test_add_co_organiser_url(self):
        self.assertEqual(self.player1_winner_url,
                         f'/{self.club.name}/tournament/{self.tournament.name}/{self.current_match.id}/enter_result/player1')

    def test_successful_enter_player1_winner(self):
        response = self.client.get(self.player1_winner_url)
        self.current_match.refresh_from_db()
        self.assertRedirects(response, self.show_schedule_url, status_code=302, target_status_code=200)
        self.assertEqual(self.current_match.get_winner(), self.current_match.get_player1())
        self.assertFalse(self.current_match.is_open())

    def test_successful_enter_player2_winner(self):
        response = self.client.get(self.player2_winner_url)
        self.current_match.refresh_from_db()
        self.assertRedirects(response, self.show_schedule_url, status_code=302, target_status_code=200)
        self.assertEqual(self.current_match.get_winner(), self.current_match.get_player2())
        self.assertFalse(self.current_match.is_open())

    def test_successful_enter_draw(self):
        response = self.client.get(self.draw_url)
        self.current_match.refresh_from_db()
        self.assertRedirects(response, self.show_schedule_url, status_code=302, target_status_code=200)
        self.assertEqual(self.current_match.get_winner(), None)
        self.assertFalse(self.current_match.is_open())

    def test_redirects_when_finished(self):
        self.tournament._set_finished()
        response = self.client.get(self.draw_url, follow=True)
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "The tournament is already finished!", messages.WARNING)

    def test_enter_forbidden_draw(self):
        tournament = Tournament.objects.get(name="Test_Tournament2")
        club = Club.objects.get(name="Test_Club2")
        self.client.login(email=club.owner.email, password='Password123')
        tournament_tester = TournamentGroupTester(tournament)
        tournament._set_deadline_now()
        tournament.start_tournament()
        final_match = tournament.get_current_schedule()[0]
        url = reverse('enter_result',
                      kwargs={'club_name': club.name, 'tournament_name': tournament.name,
                              'match_id': final_match.id, 'result': "draw"})
        response = self.client.get(url, follow=True)
        show_schedule_url = reverse('show_schedule',
                                        kwargs={'club_name': club.name, 'tournament_name': tournament.name})
        self.assertRedirects(response, show_schedule_url , status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "You cannot enter a draw result for an elimination round", messages.WARNING)

    def test_enter_result_on_non_existing_match(self):
        bad_url = reverse('enter_result',
                               kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name,
                                       'match_id': 9999, 'result': "draw"})
        response = self.client.get(bad_url, follow=True)
        self.assertRedirects(response, self.show_schedule_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "The match you are looking for doesn't exist", messages.ERROR)

    def test_enter_result_on_existing_wrong_match(self):
        other_match = Match.objects.get(pk=2)
        bad_url = reverse('enter_result',
                               kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name,
                                       'match_id': other_match.id, 'result': "draw"})
        response = self.client.get(bad_url, follow=True)
        self.assertRedirects(response, self.show_schedule_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "This match is not part of the requested tournament", messages.WARNING)

    def test_enter_result_with_wrong_result(self):
        bad_url = reverse('enter_result',
                          kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name,
                                  'match_id': self.current_match.id, 'result': "invalid"})
        response = self.client.get(bad_url, follow=True)
        self.assertRedirects(response, self.show_schedule_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "This result is not valid", messages.WARNING)

    def test_enter_result_with_wrong_club(self):
        bad_url = reverse('enter_result',
                          kwargs={'club_name': "blabla", 'tournament_name': self.tournament.name,
                                  'match_id': self.current_match.id, 'result': "draw"})
        response = self.client.get(bad_url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "The club you are looking for does not exist!", messages.ERROR)

    def test_enter_result_with_wrong_tournament(self):
        bad_url = reverse('enter_result',
                          kwargs={'club_name': self.club.name, 'tournament_name': "oops",
                                  'match_id': self.current_match.id, 'result': "draw"})
        response = self.client.get(bad_url, follow=True)
        self.assertRedirects(response, self.show_club_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "The tournament you are looking for does not exist!", messages.ERROR)

    def test_enter_result_when_deadline_not_passed(self):
        self.tournament._set_deadline_future()
        response = self.client.get(self.player1_winner_url, follow=True)
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "The deadline is not yet passed!", messages.WARNING)

    def test_co_organiser_can_enter_results(self):
        self.tournament_tester.make_co_organiser(self.co_organiser)
        self.client.login(email=self.co_organiser.email, password='Password123')
        response = self.client.get(self.player2_winner_url, follow=True)
        self.assertRedirects(response, self.show_schedule_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_participant_cannot_enter_results(self):
        self.tournament_tester.make_participant(self.co_organiser)
        self.client.login(email=self.co_organiser.email, password='Password123')
        response = self.client.get(self.player2_winner_url, follow=True)
        self.assertRedirects(response, self.show_schedule_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "Only the organiser and co-organisers can enter results", messages.WARNING)

    def test_non_participant_cannot_enter_results(self):
        self.client.login(email=self.random_member.email, password='Password123')
        response = self.client.get(self.player2_winner_url, follow=True)
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 2)
        self.assertEqual(messages_list[0].level, messages.WARNING)
        self.assertEqual(messages_list[0].message, "Only the organiser and co-organisers can enter results")

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.player1_winner_url)
        redirect_url = reverse_with_next('log_in', reverse('enter_result', kwargs={'club_name': self.club.name, 'tournament_name': self.tournament.name,
                                                  'match_id': self.current_match.id, 'result': "player1"}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _assert_response_redirect(self, response):
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_valid_response(self, response):
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def _assert_warning_message_displayed(self, response, message, level):
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, level)
        self.assertEqual(messages_list[0].message, message)

