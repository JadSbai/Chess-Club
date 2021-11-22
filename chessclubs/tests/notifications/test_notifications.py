"""Unit tests for the notifications."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from notifications.signals import notify

from chessclubs.models import User
from notifications.models import Notification
from notifications.utils import slug2id


class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'chessclubs/tests/fixtures/default_user.json',
        'chessclubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')

    def test_sending_notification(self):
        count_before = self.user.notifications.unread().size()
        notify.send(self.user, recipient=self.user, verb="test")
        count_after = self.user.notifications.unread().size()
        self.assertEqual(count_before+1, count_after)


    def test_reading_notification(self):
        notify.send(self, recipient=self.user, verb="test")
        self.user.notifications.unread().mark_all_as_read()
        count = self.user.notifications.unread().size()
        self.assertEqual(count, 0)


