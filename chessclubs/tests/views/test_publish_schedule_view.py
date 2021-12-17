"""Tests of publish schedule view"""

from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club, Tournament
from chessclubs.tests.helpers import ClubGroupTester, reverse_with_next, TournamentGroupTester, _create_test_players
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.contrib import messages
from with_asserts.mixin import AssertHTMLMixin


class PublishScheduleViewTestCase(TestCase, AssertHTMLMixin):
    """Test Suites of publish_schedule view"""
    
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json',
                'chessclubs/tests/fixtures/default_club.json',
                'chessclubs/tests/fixtures/default_tournament.json',
                ]

    @classmethod
    def setUpTestData(cls):
        cls.organiser = User.objects.get(email='johndoe@example.org')
        cls.member = User.objects.get(email='janedoe@example.org')
        cls.tournament = Tournament.objects.get(name="Test_Tournament")
        cls.club = Club.objects.get(name="Test_Club")
        _create_test_players(4, cls.club, cls.tournament)
        cls.group_tester = ClubGroupTester(cls.club)
        cls.tournament_tester = TournamentGroupTester(cls.tournament)
        cls.group_tester.make_member(cls.member)
        cls.url = reverse('publish_schedule', kwargs={'club_name':cls.club.name, 'tournament_name': cls.tournament.name})
        cls.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        cls.show_tournament_url = reverse('show_tournament', kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})
        cls.show_schedule_url = reverse('show_schedule',
                                        kwargs={'club_name': cls.club.name, 'tournament_name': cls.tournament.name})

    def setUp(self):
        self.client.login(email=self.organiser.email, password='Password123')
        self.tournament._set_deadline_now()

    def test_publish_schedule_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/tournament/{self.tournament.name}/publish_schedule/')

    def test_successful_publish_schedule(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.show_schedule_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        self.tournament.refresh_from_db()
        self.assertTrue(self.tournament.is_published())
        self.assertFalse(self.tournament.has_started())
        self.assertEqual(len(self.tournament.get_current_schedule()), 2)

    def test_publish_schedule_of_wrong_tournament(self):
        bad_url = reverse('publish_schedule', kwargs={'club_name': self.club.name, 'tournament_name': "oops"})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('show_club', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The tournament you are looking for does not exist!")

    def test_wrong_club_publish_schedule(self):
        bad_url = reverse('publish_schedule', kwargs={'club_name': "blabla", 'tournament_name': self.tournament.name})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_notification_sent(self):
        participant = self.tournament.participants_list()[0].user
        notifications = len(participant.notifications.unread())
        self.client.get(self.url)
        last_notification = participant.notifications.unread()[0].description
        self.assertEqual(len(participant.notifications.unread()), notifications+1)
        self.assertEqual(last_notification, f"The schedule for tournament {self.tournament.name} is now published!")

    def test_mark_as_read_published(self):
        self.client.get(self.url)
        participant = self.tournament.participants_list()[0].user
        self.client.login(email=participant.email, password='Password123')
        last_notification = participant.notifications.unread()[0]
        read_notif_url = reverse('mark_as_read', kwargs={'slug': last_notification.slug})
        response = self.client.get(read_notif_url, follow=True)
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)

    def test_publish_schedule_when_deadline_not_passed(self):
        self.tournament._set_deadline_future()
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "The deadline is not yet passed!", messages.WARNING)

    def test_publish_schedule_when_tournament_started(self):
        self.tournament.start_tournament()
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.show_tournament_url, status_code=302, target_status_code=200)
        self._assert_warning_message_displayed(response, "The tournament has already started!", messages.WARNING)

    def test_organiser_can_publish_schedule(self):
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_co_organiser_cannot_publish_schedule(self):
        self.client.login(email=self.member.email, password='Password123')
        self.tournament_tester.make_co_organiser(self.member)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_participant_cannot_publish_schedule(self):
        self.client.login(email=self.member.email, password='Password123')
        self.tournament_tester.make_participant(self.member)
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_non_participant_cannot_publish_schedule(self):
        self.client.login(email=self.member.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_non_logged_in_redirects(self):
        self.client.logout()
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('publish_schedule', kwargs={'club_name':self.club.name, 'tournament_name': self.tournament.name}))
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
