from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User, Club
from chessclubs.tests.helpers import reverse_with_next, ClubGroupTester
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN

class ShowUserTest(TestCase):

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json',
        'chessclubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.other_user = User.objects.get(email='petrapickles@example.org')
        self.target_user = User.objects.get(email='janedoe@example.org')
        self.club = Club.objects.get(name="Test_Club")
        self.group_tester = ClubGroupTester(self.club)
        self.club.add_member(self.target_user)
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_name': self.club.name})
        self.redirect_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)

    def test_show_user_url(self):
        self.assertEqual(self.url, f'/{self.club.name}/user/{self.target_user.id}')

    def test_get_show_user_with_valid_id_and_club(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "Jane Doe")

    def test_get_show_user_with_own_id(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('show_user', kwargs={'user_id': self.user.id, 'club_name': self.club.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertContains(response, "John Doe")

    def test_get_show_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_wrong_user(self):
        self.client.login(email=self.user.email, password='Password123')
        bad_url = reverse('show_user', kwargs={'club_name': self.club.name, 'user_id': 2000})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse('user_list', kwargs={'club_name':self.club.name})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The user you are looking for does not exist!")

    def test_show_user_in_wrong_club(self):
        self.client.login(email=self.user.email, password='Password123')
        bad_url = reverse('show_user', kwargs={'club_name': "blabla", 'user_id': self.target_user.id})
        response = self.client.get(bad_url, follow=True)
        target_url = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing_page.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertEqual(messages_list[0].message, "The club you are looking for does not exist!")

    def test_applicant_cannot_access_the_user_page(self):
        self.group_tester.make_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_accepted_applicant_cannot_access_the_user_page(self):
        self.group_tester.make_accepted_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_denied_applicant_cannot_access_the_user_page(self):
        self.group_tester.make_denied_applicant(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_member_can_access_the_user_page(self):
        self.group_tester.make_member(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_officer_can_access_the_user_page(self):
        self.group_tester.make_officer(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_owner_can_access_the_user_page(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_logged_in_non_member_cannot_access_the_user_page(self):
        self.group_tester.make_authenticated_non_member(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_member_cannot_see_private_info(self):
        self.group_tester.make_member(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(response, "Chess Experience")
        self.assertNotContains(response, "Personal Statement")
        self.assertNotContains(response, "Email")

    def test_officer_can_see_private_info(self):
        self.group_tester.make_officer(self.other_user)
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, "Chess Experience")
        self.assertContains(response, "Personal Statement")
        self.assertContains(response, "Email")

    def test_owner_can_see_private_info(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, "Chess Experience")
        self.assertContains(response, "Personal Statement")
        self.assertContains(response, "Email")

    def test_owner_can_see_member_buttons(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, "Promote")

    def test_owner_can_see_officer_button(self):
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester.make_officer(self.target_user)
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, "Demote")
        self.assertContains(response, "Transfer ownership")

