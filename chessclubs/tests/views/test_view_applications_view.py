from chessclubs.models import User
from chessclubs.tests.helpers import reverse_with_next
from chessclubs.tests.helpers import GroupTester
from chessclubs.groups import groups
from notifications.models import Notification
from notifications.signals import notify
from django.test import TestCase
from django.urls import reverse

class ApplicationViewTestCase(TestCase):
    fixtures = ['chessclubs/tests/fixtures/default_user.json',
                'chessclubs/tests/fixtures/other_users.json'
                ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.user2 = User.objects.get(email = 'janedoe@example.org')
        self.client.login(email=self.user.email, password='Password123')
        self.group_tester = GroupTester()
        self.group_tester.make_applicant(self.user2)
        self.group_tester.make_officer(self.user)
        self.url = reverse('view_applications')

    def test_view_application_url(self):
        self.assertEqual(self.url, '/view_applications/')
