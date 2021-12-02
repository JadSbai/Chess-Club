"""Tests of the mark as read view."""
from django.test import TestCase
from django.urls import reverse
from notifications.signals import notify
from chessclubs.models import User
from Wildebeest.settings import REDIRECT_URL_WHEN_LOGGED_IN
from chessclubs.tests.helpers import reverse_with_next


class MarkAsReadViewTestCase(TestCase):
    """Tests of the my_profile view."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.client.login(email=self.user.email, password='Password123')
        notify.send(self.user, recipient=self.user, verb='Message',
                    description="Talking to yourself")
        self.slug = self.user.notifications.unread()[0].slug
        self.url = reverse('mark_as_read', kwargs={'slug': self.slug})
        self.redirect_url = reverse('my_applications')

    def test_notification_is_read(self):
        before_count = self.user.notifications.unread().count()
        self.assertEqual(self.user.notifications.unread()[0].description, "Talking to yourself")
        response = self.client.get(self.url)
        after_count = self.user.notifications.unread().count()
        self.assertEqual(after_count, before_count - 1)
        self.assertRedirects(response, self.redirect_url, status_code=302, target_status_code=200)
