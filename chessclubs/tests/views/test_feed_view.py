"""Tests of the feed view."""
from django.test import TestCase
from django.urls import reverse
from chessclubs.models import User
from chessclubs.tests.helpers import reverse_with_next


class FeedViewTestCase(TestCase):
    """Tests of the feed view."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('feed')

    def test_feed_url(self):
        self.assertEqual(self.url,'/feed/')

    def test_get_feed(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_profile.html')

    def test_get_feed_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)