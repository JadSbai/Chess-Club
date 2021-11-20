"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from chessclubs.forms import UserForm
from chessclubs.models import User
from chessclubs.tests.helpers import reverse_with_next

class ProfileViewTest(TestCase):
    """Test suite for the change_profile view."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.url = reverse('change_profile')
        self.form_input = {
            'first_name': 'John2',
            'last_name': 'Doe2',
            'bio': 'New bio',
            'chess_experience': 'Intermediate',
            'personal_statement': 'I am the best',
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/change_profile/')

    def test_get_profile(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertEqual(form.instance, self.user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_profile_update(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['chess_experience'] = ''
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.bio, "Hello, I'm John Doe.")
        self.assertEqual(self.user.chess_experience, "Expert")
        self.assertEqual(self.user.personal_statement, "I'm the best of the best")


    def test_succesful_profile_update(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('my_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'my_profile.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.bio, 'New bio')
        self.assertEqual(self.user.chess_experience, 'Intermediate')
        self.assertEqual(self.user.personal_statement, 'I am the best')

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
