"""Unit tests for the notifications."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notifications.signals import notify

from chessclubs.models import User
from notifications.models import Notification
from notifications.utils import slug2id


class NotificationTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.user2 = User.objects.get(email='janedoe@example.org')

    def test_sending_notification(self):
        count_before = len(self.user2.notifications.unread())
        notify.send(self.user, recipient=self.user2, verb='Message', description="Test")
        count_after = len(self.user2.notifications.unread())
        self.assertEqual(count_before+1, count_after)


    def test_reading_notification(self):
        notify.send(self.user, recipient=self.user2, verb='Message', description="Test")
        self.user2.notifications.unread().mark_all_as_read()
        count = len(self.user2.notifications.unread())
        self.assertEqual(count, 0)


