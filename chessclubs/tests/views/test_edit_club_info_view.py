"""Tests for the edit_club_info view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from chessclubs.forms import EditClubInformationForm
from chessclubs.models import User, Club
from chessclubs.tests.helpers import reverse_with_next, ClubGroupTester


class EditClubInfoViewTest(TestCase):
    """Test suite for the edit_club_info view."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',

    ]

    def setUp(self):
        self.owner = User.objects.get(email='johndoe@example.org')
        self.other_user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.club_group_tester = ClubGroupTester(self.club)
        self.url = reverse('edit_club', kwargs={'club_name': self.club.name})
        self.form_input = {
            'description': 'New Standards',
            'location': 'Zimbabwe',
        }
        self.redirect_url = reverse('show_club', kwargs={'club_name': self.club.name})

    def test_edit_club_info_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/edit_club_info/')

    def test_get_profile(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club_info.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubInformationForm))
        self.assertEqual(form.instance, self.club)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_edit_club(self):
        self.client.login(email=self.owner.email, password='Password123')
        self.form_input['location'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club_info.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubInformationForm))
        self.assertTrue(form.is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, 'Best club ever')
        self.assertEqual(self.club.location, 'London')

    def test_successful_profile_update(self):
        self.client.login(email=self.owner.email, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('show_club', kwargs={'club_name': self.club.name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, 'New Standards')
        self.assertEqual(self.club.location, 'Zimbabwe')

    def test_wrong_club_transfer(self):
        self.client.login(email=self.owner.email, password='Password123')
        bad_url = reverse('edit_club', kwargs={'club_name': "blabla"})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_applicant_cannot_edit_club_info(self):
        self.club_group_tester.make_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_accepted_applicant_cannot_edit_club_info(self):
        self.club_group_tester.make_accepted_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_denied_applicant_cannot_edit_club_info(self):
        self.club_group_tester.make_denied_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_member_cannot_edit_club_info(self):
        self.club_group_tester.make_member(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_officer_cannot_edit_club_info(self):
        self.club_group_tester.make_officer(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_response_redirect(response)

    def test_owner_can_edit_club_info(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self._assert_valid_response(response)

    def test_post_club_info_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_non_logged_is_redirected(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', reverse('edit_club', kwargs={'club_name': self.club.name}))
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _assert_response_redirect(self, response):
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def _assert_valid_response(self, response):
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
